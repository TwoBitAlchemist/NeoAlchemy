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


class UnboundedWriteOperation(RuntimeError):
    def __init__(self, obj, error_info=None):
        error = "Attempted unbounded write operation on %s object."
        error %= obj.__class__.__name__
        if error_info:
            error = '%s %s' % (error, error_info)
        super(UnboundedWriteOperation, self).__init__(error)
