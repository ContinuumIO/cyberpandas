import operator

import numpy as np

import pandas as pd
from pandas.core.arrays import ExtensionArray

from ._utils import refactorize


class NumPyBackedExtensionArrayMixin(ExtensionArray):
    @property
    def dtype(self):
        """The dtype for this extension array, IPType"""
        return self._dtype

    @classmethod
    def _constructor_from_sequence(cls, scalars):
        return cls(scalars)

    @property
    def shape(self):
        return (len(self.data),)

    def __len__(self):
        return len(self.data)

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

    def factorize(self, na_sentinel=-1):
        """Factorize an IPArray into integer labels and unique values.

        Calling :meth:`pandas.Series.factorize` or :meth:`pandas.factorize`
        will dispatch to this method.

        Parameters
        ----------
        na_sentinel : int, default -1
            The value in `labels` to use for indicating missing values in
            `self`.

        Returns
        -------
        labels : ndarray
            An integer-type ndarray the same length as `self`. Each newly-
            observed value in `self` will be assigned the next integer.
            Missing values in self are assigned `na_sentinel`.
        uniques : IPArray
            The unique values in `self` in order of appereance, not including
            the missing value ``IPv4Address('0.0.0.0')``.

        See Also
        --------
        pandas.factorize, pandas.Series.factorize

        Examples
        --------
        >>> arr = IPArray([2, 2, 0, 1, 2, 2**64 + 1])
        >>> arr
        IPArray(['0.0.0.2', '0.0.0.2', '0.0.0.0', '0.0.0.1',
                 '0.0.0.2', '::1:0:0:0:1'])

        >>> labels, uniques = arr.factorize()
        >>> labels
        array([ 0,  0, -1,  1,  0,  2])

        Notice that `uniques` does not include the missing value.
        >>> uniques
        IPArray(['0.0.0.2', '0.0.0.1', '::1:0:0:0:1'])
        """
        # OK, so here's the plan.
        # Start with factorizing `self.data`, which has two unfortunate issues
        # 1. Requires casting to object.
        # 2. Gets the NA logic wrong, since (0, 0) isn't NA to pandas.
        # For now, we can't help with 1. Maybe someday.
        # For 2, we can "fix" things with a little post-factorization cleanup.
        l, u = pd.factorize(self.data)
        mask = self.isna()
        any_na = mask.any()

        if any_na:
            first_na = mask.argmax()
            refactorize(l, first_na, na_sentinel=na_sentinel)  # inplace op

        # u is an ndarray of tuples. Go to our record type, then an IPArray
        u2 = type(self)((u.astype(self.dtype._record_type)))
        # May have a missing value.
        if any_na:
            u2 = u2[~u2.isna()]
        return l, u2
