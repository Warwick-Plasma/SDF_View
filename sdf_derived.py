import sdf
import sdf_helper as sh
import numpy

class derived_variable(object):
    _data = None
    alwayscache = False
    nevercache = False

    def __init__(self, name="Blank", datafunction=None, backingdata=None,
                 grid=None, grid_mid=None, dims=None, units=None):
        self.name = name
        self.backingdata = backingdata
        self.datafunction = datafunction
        self.grid = grid
        self.grid_mid = grid_mid
        self.dims = dims
        self.units = units
        # If bits that can be sensibly autoconstructed are missing, try
        # to pick them up
        if grid is None:
            try:
                self.grid = self.backingdata.grid
            except:
                pass
        if grid_mid is None:
            try:
                self.grid_mid = self.backingdata.grid_mid
            except:
                pass
        if dims is None:
            try:
                self.dims = self.backingdata.dims
            except:
                pass
        if units is None:
            try:
                self.units = self.backingdata.units
            except:
                pass

    def get_data(self):
        if self._data is not None:
            return self._data
        data, cache = self._datafunction(self, self._backingdata)
        if (cache or self.alwayscache) and not self.nevercache:
            self._data = data
        return data

    def set_data(self, value):
        self._data = value

    def get_backingdata(self):
        return self._backingdata

    def set_backingdata(self, value):
        self._data = None
        self._backingdata = value

    def get_datafunction(self):
        return self._datafunction

    def set_datafunction(self, value):
        self._data = None
        self._datafunction = value

    def get_grid(self):
        return self._grid

    def set_grid(self, value):
        self._data = None
        self._grid = value

    def get_grid_mid(self):
        return self._grid_mid

    def set_grid_mid(self, value):
        self._data = None
        self._grid_mid = value

    data = property(get_data, set_data)
    backingdata = property(get_backingdata, set_backingdata)
    datafunction = property(get_datafunction, set_datafunction)
    grid = property(get_grid, set_grid)
    grid_mid = property(get_grid_mid, set_grid_mid)


class derived_grid(object):
    _data = None
    _datafunction = None
    _backingdata = None

    def __init__(self, basegrid):
        # These are explicit copies because grid doesnt implement
        # __dict__properly
        if basegrid is not None:
            self.data = list(basegrid.data)
            self.data_length = basegrid.data_length
            self.datatype = basegrid.datatype
            self.dims = list(basegrid.dims)
            self.extents = basegrid.extents
            self.geometry = basegrid.geometry
            self.labels = list(basegrid.labels)
            self.units = list(basegrid.units)
            self.stagger = basegrid.stagger
        else:
            self.data = []
            self.data_length = 0
            self.datatype = 0
            self.dims = []
            self.extents = []
            self.geometry = 0
            self.labels = []
            self.units = []
            self.stagger = 0

    def set_datafunction(self, value):
        self._datafunction = value

    def get_datafunction(self, value):
        return self._datafunction

    def set_data(self, value):
        self._data = value

    def get_data(self):
        if(self._data is not None):
            return self._data
        else:
            return self._datafunction(self._backingdata)

    def set_backingdata(self, value):
        self._backingdata = value

    def get_backingdata(self):
        return self._backingdata

    data = property(get_data, set_data)
    backingdata = property(get_backingdata, set_backingdata)
    datafunction = property(get_datafunction, set_datafunction)


def _average(caller, backingdata, direction):
    return numpy.sum(backingdata.data, direction) / backingdata.dims[direction],
           True


def _sum(caller, backingdata, direction):
    return numpy.sum(backingdata.data, direction), True


def _abs_sq(caller, backingdata):
    return numpy.abs(numpy.square(backingdata.data)), False


def _slice(caller, backingdata, slice):
    return numpy.squeeze(backingdata.data[slice]), False


def _multiply(caller, backingdata, secondarray):
    return numpy.multiply(backingdata.data, secondarray), False


def _divide(caller, backingdata, secondarray):
    return numpy.divide(backingdata.data, secondarray), False


def _add(caller, backingdata, secondarray):
    return numpy.add(backingdata.data, secondarray), False


def _subtract(caller, backingdata, secondarray):
    return numpy.subtract(backingdata.data, secondarray), False


def _arithmetic(base, secondarray, function, symbol, **kwargs):
    if 'name' in kwargs:
        name = kwargs['name']
    else:
        name = None

    if name is None:
        try:
            name = base.name + symbol + secondarray.name
        except:
            try:
                alen = len(secondarray)
                if alen == 1:
                    name = base.name + symbol + ' constant'
                else:
                    name = base.name + symbol + ' array'
            except TypeError:
                name = base.name + symbol + ' constant'
            except:
                return None

    kwargs['name'] = name
    # Check if have SDF object or bare array
    try:
        temp = secondarray.name
        l = lambda caller, backingdata, a2=secondarray.data:
                function(caller, backingdata, a2)
    except:
        l = lambda caller, backingdata, a2=secondarray:
                function(caller, backingdata, a2)

    # Finally create the actual derived variable and return it
    dv = derived_variable(datafunction=l, backingdata=base, grid=base.grid,
                          grid_mid=base.grid_mid, dims=base.dims, **kwargs)
    return dv


def is_lagrangian(var):
    try:
        # For a variable
        val = numpy.ndim(var.grid.data[0]) != 1
    except:
        try:
            # For a grid
            val = numpy.ndim(var.data[0]) != 1
        except:
            # Can't say anything useful, return None
            val = None
    return val


# This routine takes a grid object and crops out directions that are not listed
# in the "direction" collection. Returns a new grid object
def get_reduced_grid(basegrid, direction=[0,1]):
    ngrid = derived_grid(None)
    try:
        temp = direction[0]
    except:
        try:
            direction = [direction]
        except:
            return None

    ndims = len(basegrid.dims)
    begins = basegrid.extents[0:ndims]
    ends = basegrid.extents[ndims:2*ndims]
    nbegin = []
    nend = []
    slices = []
    ngrid.data_length = basegrid.data_length
    ngrid.datatype = basegrid.datatype
    ngrid.geometry = basegrid.geometry
    ngrid.stagger = basegrid.stagger
    for cdir in direction:
        ngrid.data.append(basegrid.data[cdir])
        ngrid.dims.append(basegrid.dims[cdir])
        nbegin.append(begins[cdir])
        nend.append(ends[cdir])
        ngrid.extents.append(basegrid.extents[cdir])
        ngrid.labels.append(basegrid.labels[cdir])
        ngrid.units.append(basegrid.units[cdir])
    ngrid.extents = nbegin + nend
    return ngrid


def tuple_to_slice(slices):
    subscripts = []
    for val in slices:
        start = val[0]
        end = val[1]
        if end is not None:
            end = end + 1
        subscripts.append(slice(start, end, 1))
    subscripts = tuple(subscripts)
    return subscripts


def trim_grid(basegrid, slices):
    lag = is_lagrangian(basegrid)
    ngrid = derived_grid(basegrid)
    subscripts = tuple_to_slice(slices)
    ndims = 0
    dimskeep = []
    mins = []
    maxs = []
    for x in range(0, len(slices)):
        if not lag:
            naxis = ngrid.data[x][subscripts[x]]
        else:
            naxis = ngrid.data[x][subscripts]
        print(numpy.shape(naxis))
        l = len(naxis)
        mins.append(numpy.min(naxis))
        maxs.append(numpy.max(naxis))
        if (l != 1 or lag):
            ngrid.data[x] = naxis
            ngrid.dims[x] = l
            ndims = ndims + 1
            dimskeep.append(x)
    ngrid.extents = mins + maxs
    ngrid = get_reduced_grid(ngrid, direction=dimskeep)
    return ngrid


def average(base, direction=0, **kwargs):
    if 'name' in kwargs:
        name = kwargs['name']
    else:
        name = None
    if is_lagrangian(base):
        print("Cannot automatically average over a Lagrangian grid")
        return None
    if name is None:
        name = 'Average(' + base.name + ')'

    # Get the actual dimensions of the final array
    dims = list(base.dims)
    del dims[direction]

    # Produce an array of all remaining dimension indices and produce the grid
    rdims = range(0, len(base.dims))
    del rdims[direction]
    ngrid = get_reduced_grid(base.grid, direction=rdims)
    ngrid_mid = get_reduced_grid(base.grid_mid, direction=rdims)

    # Use a lambda as a closure to call the actual average function
    l = lambda caller, backingdata, direction=direction:
            _average(caller, backingdata, direction)

    # Finally create the actual derived variable and return it
    dv = derived_variable(name=name, datafunction=l, backingdata=base,
                          grid=ngrid, grid_mid=ngrid_mid, dims=dims, **kwargs)
    return dv


def sum(base, direction=0, **kwargs):
    if 'name' in kwargs:
        name = kwargs['name']
    else:
        name = None
    if is_lagrangian(base):
        print("Cannot automatically sum over a Lagrangian grid")
        return None
    if name is None:
        name = 'Sum(' + base.name + ')'
    kwargs['name'] = name
    # Get the actual dimensions of the final array
    dims = list(base.dims)
    del dims[direction]

    # Produce an array of all remaining dimension indices and produce the grid
    rdims = range(0, len(base.dims))
    del rdims[direction]
    ngrid = get_reduced_grid(base.grid, direction=rdims)
    ngrid_mid = get_reduced_grid(base.grid_mid, direction=rdims)

    # Use a lambda as a closure to call the actual sum function
    l = lambda caller, backingdata, direction=direction:
            _sum(caller, backingdata, direction)

    # Finally create the actual derived variable and return it
    dv = derived_variable(name=name, datafunction=l, backingdata=base,
                          grid=ngrid, grid_mid=ngrid_mid, dims=dims, **kwargs)
    return dv


def abs_sq(base, **kwargs):
    if 'name' in kwargs:
        name = kwargs['name']
    else:
        name = None
    if name is None:
        name = 'Abs_Sq(' + base.name + ')'
    kwargs['name'] = name
    dv = derived_variable(name=name, datafunction=_abs_sq, backingdata=base,
                          grid=base.grid, grid_mid=base.grid_mid,
                          dims=base.dims, **kwargs)
    return dv


def multiply(base, secondarray, **kwargs):
    dv = _arithmetic(base, secondarray, _multiply, '*', **kwargs)
    return dv


def divide(base, secondarray, **kwargs):
    dv = _arithmetic(base, secondarray, _divide, '\\', **kwargs)
    return dv


def add(base, secondarray, **kwargs):
    dv = _arithmetic(base, secondarray, _add, '+', **kwargs)
    return dv


def subtract(base, secondarray, **kwargs):
    dv = _arithmetic(base, secondarray, _subtract, '-', **kwargs)
    return dv


# Function to create a subarray of an array
# If the subarray is 1 element in any direction then
# The array is reduced in dimensionality
def subarray(base, slices, name=None):
    if (len(slices) != len(base.dims)):
        print("Must specify a range in all dimensions")
        return None
    dims = []
    # Construct the lengths of the subarray
    for x in range(0, len(slices)):
        begin = slices[x][0]
        end = slices[x][1]
        if begin is None:
            begin = 0
        if end is None:
            end = base.dims[x]
        if (end-begin != 0):
            dims.append(end-begin)

    ngrid = trim_grid(base.grid, slices)
    ngrid_mid = trim_grid(base.grid_mid, slices)
    subscripts = tuple_to_slice(slices)
    if name is None:
        name = 'Slice(' + base.name + ')'
    l = lambda caller, backingdata, a2=subscripts:
        _slice(caller, backingdata, a2)
    # Finally create the actual derived variable and return it
    dv = derived_variable(name, datafunction=l, backingdata=base, grid=ngrid,
                          grid_mid=ngrid_mid, dims=dims)
    return dv
