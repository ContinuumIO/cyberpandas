import operator

import numpy as np

from pandas.core.arrays import ExtensionArray


class NumPyBackedExtensionArrayMixin(ExtensionArray):
    @property
    def dtype(self):
        """The dtype for this extension array, IPType"""
        return self._dtype

    @classmethod
    def _from_sequence(cls, scalars, dtype=None, copy=False):
        return cls(scalars, dtype=dtype)

    @classmethod
    def _from_factorized(cls, values, original):
        return cls(values)

    @property
    def size(self):
        return self.data.size

    @property
    def shape(self):
        return self.data.shape

    @property
    def ndim(self):
        return len(self.shape)

    def __len__(self):
        return self.shape[0]

    def __getitem__(self, *args):
        result = operator.getitem(self.data, *args)
        if isinstance(result, tuple):
            return self._box_scalar(result)
        elif result.ndim == 0:
            return self._box_scalar(result.item())
        else:
            return type(self)(result)

    def setitem(self, indexer, value):
        """Set the 'value' inplace.
        """
        # I think having a separate than __setitem__ is good
        # since we have to return here, but __setitem__ doesn't.
        self[indexer] = value
        return self

    @property
    def nbytes(self):
        return self._itemsize * len(self)

    def _formatting_values(self):
        return np.array(self._format_values(), dtype='object')

    def copy(self, deep=False):
        return type(self)(self.data.copy())

    @classmethod
    def _concat_same_type(cls, to_concat):
        return cls(np.concatenate([array.data for array in to_concat]))

    def tolist(self):
        return self.data.tolist()

    def argsort(self, axis=-1, kind='quicksort', order=None):
        return self.data.argsort()

    def unique(self):
        # type: () -> ExtensionArray
        # https://github.com/pandas-dev/pandas/pull/19869
        _, indices = np.unique(self.data, return_index=True)
        data = self.data.take(np.sort(indices))
        return self._from_ndarray(data)
