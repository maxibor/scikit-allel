# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division


import unittest
import numpy as np
import bcolz
import h5py
from nose.tools import assert_raises, eq_ as eq


from allel.model.ndarray import GenotypeArray
from allel.test.tools import assert_array_equal as aeq
from allel.test.test_model_api import GenotypeArrayInterface, \
    diploid_genotype_data, triploid_genotype_data
import allel.model.chunked
from allel.model.chunked import GenotypeChunkedArray, numpy_backend, \
    bcolz_backend, h5mem_backend, h5tmp_backend, bcolz_gzip1_backend, \
    bcolztmp_backend


class GenotypeChunkedArrayTests(GenotypeArrayInterface, unittest.TestCase):

    _class = GenotypeChunkedArray
    
    def setUp(self):
        allel.model.chunked.default_backend = numpy_backend
        
    def setup_instance(self, data):
        data = allel.model.chunked.default_backend.create(data)
        return GenotypeChunkedArray(data)

    def test_constructor(self):

        # missing data arg
        with assert_raises(TypeError):
            # noinspection PyArgumentList
            GenotypeChunkedArray()

        # data has wrong dtype
        data = 'foo bar'
        with assert_raises(ValueError):
            GenotypeChunkedArray(data)

        # data has wrong dtype
        data = np.array([4., 5., 3.7])
        with assert_raises(ValueError):
            GenotypeChunkedArray(data)

        # data has wrong dimensions
        data = np.array([1, 2, 3])
        with assert_raises(ValueError):
            GenotypeChunkedArray(data)

        # data has wrong dimensions
        data = np.array([[1, 2], [3, 4]])  # use HaplotypeChunkedArray instead
        with assert_raises(ValueError):
            GenotypeChunkedArray(data)

        # diploid data (typed)
        g = self.setup_instance(np.array(diploid_genotype_data, dtype='i1'))
        aeq(diploid_genotype_data, g)
        eq(np.int8, g.dtype)

        # polyploid data (typed)
        g = self.setup_instance(np.array(triploid_genotype_data, dtype='i1'))
        aeq(triploid_genotype_data, g)
        eq(np.int8, g.dtype)

    def test_backend(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, np.ndarray)

    def test_slice_types(self):

        g = self.setup_instance(np.array(diploid_genotype_data, dtype='i1'))

        # row slice
        s = g[1:]
        self.assertNotIsInstance(s, GenotypeChunkedArray)
        self.assertIsInstance(s, GenotypeArray)

        # col slice
        s = g[:, 1:]
        self.assertNotIsInstance(s, GenotypeChunkedArray)
        self.assertIsInstance(s, GenotypeArray)

        # row index
        s = g[0]
        self.assertNotIsInstance(s, GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # col index
        s = g[:, 0]
        self.assertNotIsInstance(s, GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # ploidy index
        s = g[:, :, 0]
        self.assertNotIsInstance(s, GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # item
        s = g[0, 0, 0]
        self.assertNotIsInstance(s, GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.int8)

    def test_take(self):
        g = self.setup_instance(diploid_genotype_data)
        # take variants not in original order
        # not supported for carrays
        indices = [2, 0]
        with assert_raises(NotImplementedError):
            g.take(indices, axis=0)


class GenotypeChunkedArrayTestsBColzBackend(GenotypeChunkedArrayTests):

    def setUp(self):
        allel.model.chunked.default_backend = bcolz_backend

    def test_backend(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, bcolz.carray)
        assert g.data.rootdir is None


class GenotypeChunkedArrayTestsBColzGzipBackend(GenotypeChunkedArrayTests):

    def setUp(self):
        allel.model.chunked.default_backend = bcolz_gzip1_backend

    def test_backend(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, bcolz.carray)
        eq('zlib', g.data.cparams.cname)
        eq(1, g.data.cparams.clevel)


class GenotypeChunkedArrayTestsBColzTmpBackend(GenotypeChunkedArrayTests):

    def setUp(self):
        allel.model.chunked.default_backend = bcolztmp_backend

    def test_backend(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, bcolz.carray)
        assert g.data.rootdir is not None


class GenotypeChunkedArrayTestsH5tmpBackend(GenotypeChunkedArrayTests):

    def setUp(self):
        allel.model.chunked.default_backend = h5tmp_backend

    def test_backend(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, h5py.Dataset)


class GenotypeChunkedArrayTestsH5memBackend(GenotypeChunkedArrayTests):

    def setUp(self):
        allel.model.chunked.default_backend = h5mem_backend

    def test_backend(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, h5py.Dataset)
