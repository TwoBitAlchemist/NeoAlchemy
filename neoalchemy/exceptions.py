class DetachedObjectError(TypeError):
    def __init__(self, obj, action='write'):
        error = "Can't %s %s object when not attached to any graph instance."
        cls = obj.__class__.__name__
        super(DetachedObjectError, self).__init__(error % (action, cls))


class ImmutableAttributeError(AttributeError):
    def __init__(self, name, obj):
        error = "Can't reset immutable attribute '%s' on %s object."
        cls = obj.__class__.__name__
        super(ImmutableAttributeError, self).__init__(error % (name, cls))
