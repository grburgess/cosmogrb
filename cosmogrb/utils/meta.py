class Parameter(object):
    def __init__(self, dict_name, default=None, vmin=None, vmax=None):

        self.name = None
        self._vmin = vmin
        self._vmax = vmax
        self._default = default
        self._dict_name = dict_name
        self._current_value = default
        
        
    @property
    def default(self):
        return self._default

    def __get__(self, obj, type=None) -> object:

        try:

            value = getattr(obj, self._dict_name)[self.name]

        except:
            getattr(obj, self._dict_name)[self.name] = self._default

            value = getattr(obj, self._dict_name)[self.name]

        if not isinstance(value, str):
            if self._vmin is not None:
                assert (
                    value >= self._vmin
                ), f"trying to set {self.name} to a value below {self._vmin} is not allowed"

            if self._vmax is not None:
                assert (
                    value <= self._vmax
                ), f"trying to set {self.name} to a value above {self._vmax} is not allowed"

            
            
        return value

    def __set__(self, obj, value) -> None:

        if not isinstance(value, str):
            if self._vmin is not None:
                assert (
                    value >= self._vmin
                ), f"trying to set {self.name} to a value below {self._vmin} is not allowed"

            if self._vmax is not None:
                assert (
                    value <= self._vmax
                ), f"trying to set {self.name} to a value above {self._vmax} is not allowed"

        getattr(obj, self._dict_name)[self.name] = value
        self._current_value = value
        

class SourceParameter(Parameter):
    def __init__(self, default=None, vmin=None, vmax=None):

        super(SourceParameter, self).__init__("_source_params", default, vmin, vmax)


class RequiredParameter(Parameter):
    def __init__(self, default=None, vmin=None, vmax=None):

        super(RequiredParameter, self).__init__("_required_params", default, vmin, vmax)


class GRBMeta(type):
    def __new__(mcls, name, bases, attrs):

        # build the list to make sure things are
        # attached
        
        if "_parameter_names" not in attrs:
            attrs["_parameter_names"] = []

        if "_required_names" not in attrs:

            attrs["_required_names"] = []

        # now, we want to make sure that subclasses
        # inherit the parameter names. Thus, we look
        # up the bases of the current class and
        # grab any that were attached. 

        # in the future, I may want to remove the parameter
        # names from this so that they are not inheritied
            
        for base in bases:

            try:
                attrs["_parameter_names"].extend(base._parameter_names)

            except:

                pass

            try:

                attrs["_required_names"].extend(base._required_names)

            except:

                pass

        cls = super().__new__(mcls, name, bases, attrs)

        # Compute set of abstract method names
        abstracts = {
            name
            for name, value in attrs.items()
            if getattr(value, "__isabstractmethod__", False)
        }
        for base in bases:
            for name in getattr(base, "__abstractmethods__", set()):
                value = getattr(cls, name, None)
                if getattr(value, "__isabstractmethod__", False):
                    abstracts.add(name)
        cls.__abstractmethods__ = frozenset(abstracts)

        ### parameters

        for k, v in attrs.items():

            if isinstance(v, SourceParameter):
                v.name = k
                attrs["_parameter_names"].append(k)

            if isinstance(v, RequiredParameter):

                v.name = k
                attrs["_required_names"].append(k)

        return cls

    def __subclasscheck__(cls, subclass):
        """Override for issubclass(subclass, cls)."""
        if not isinstance(subclass, type):
            raise TypeError("issubclass() arg 1 must be a class")
        # Check cache

        # Check the subclass hook
        ok = cls.__subclasshook__(subclass)
        if ok is not NotImplemented:
            assert isinstance(ok, bool)
            if ok:
                cls._abc_cache.add(subclass)
            else:
                cls._abc_negative_cache.add(subclass)
            return ok
        # Check if it's a direct subclass
        if cls in getattr(subclass, "__mro__", ()):
            cls._abc_cache.add(subclass)
            return True
        # Check if it's a subclass of a registered class (recursive)
        for rcls in cls._abc_registry:
            if issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                return True
        # Check if it's a subclass of a subclass (recursive)
        for scls in cls.__subclasses__():
            if issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                return True
        # No dice; update negative cache
        cls._abc_negative_cache.add(subclass)
        return False
