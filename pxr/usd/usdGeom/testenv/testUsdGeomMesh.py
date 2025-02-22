#!/pxrpythonsubst
#
# Copyright 2017 Pixar
#
# Licensed under the terms set forth in the LICENSE.txt file available at
# https://openusd.org/license.

from pxr import Usd, UsdGeom, Vt
import unittest


class TestUsdGeomMesh(unittest.TestCase):


    def test_ValidateTopology(self):
        """Tests helpers for validating mesh topology."""
        
        # sum(vertexCounts) != len(vertexIndices)
        faceVertexIndices = Vt.IntArray([0,1,2])
        faceVertexCounts = Vt.IntArray([2,2])

        valid,why = UsdGeom.Mesh.ValidateTopology(faceVertexIndices,
                                                  faceVertexCounts,
                                                  numPoints=3)

        self.assertFalse(valid)
        # Make sure we have a reason.
        self.assertTrue(why)

        # Negative vertex indices.
        faceVertexIndices = Vt.IntArray([0,-1,1])
        faceVertexCounts = Vt.IntArray([3])

        valid,why = UsdGeom.Mesh.ValidateTopology(faceVertexIndices,
                                                  faceVertexCounts,
                                                  numPoints=3)
        self.assertFalse(valid)
        # Make sure we have a reason.
        self.assertTrue(why)

        # Out of range vertex indices.
        faceVertexIndices = Vt.IntArray([1,2,3])
        faceVertexCounts = Vt.IntArray([3])

        valid,why = UsdGeom.Mesh.ValidateTopology(faceVertexIndices,
                                                  faceVertexCounts,
                                                  numPoints=3)

        self.assertFalse(valid)
        # Make sure we have a reason.
        self.assertTrue(why)

        # Valid topology.
        faceVertexIndices = Vt.IntArray([0,1,2,3,4,5])
        faceVertexCounts = Vt.IntArray([3,3])

        valid,why = UsdGeom.Mesh.ValidateTopology(faceVertexIndices,
                                                  faceVertexCounts,
                                                  numPoints=6)
        self.assertTrue(valid)
        # Shoult not have set a reason.
        self.assertFalse(why)

    def test_ComputeFaceCount(self):
        stage = Usd.Stage.Open('mesh.usda')
        unset = UsdGeom.Mesh.Get(stage, '/UnsetVertexCounts')
        blocked = UsdGeom.Mesh.Get(stage, '/BlockedVertexCounts')
        empty = UsdGeom.Mesh.Get(stage, '/EmptyVertexCounts')
        timeSampled = UsdGeom.Mesh.Get(stage, '/TimeSampledVertexCounts')
        timeSampledAndDefault = UsdGeom.Mesh.Get(stage, '/TimeSampledAndDefaultVertexCounts')

        testTimeSamples = [
            (unset, Usd.TimeCode.EarliestTime(), 0),
            (blocked, Usd.TimeCode.EarliestTime(), 0),
            (empty, Usd.TimeCode.EarliestTime(), 0),
            (timeSampled, Usd.TimeCode.EarliestTime(), 3),
            (timeSampledAndDefault, Usd.TimeCode.EarliestTime(), 5)]
        testDefaults = [
            (unset, 0),
            (blocked, 0),
            (empty, 0),
            (timeSampled, 0),
            (timeSampledAndDefault, 4)]

        for (schema, timeCode, expected) in testTimeSamples:
            self.assertTrue(schema)
            self.assertEqual(schema.GetFaceCount(timeCode), expected)
        for (schema, expected) in testDefaults:
            self.assertTrue(schema)
            self.assertEqual(schema.GetFaceCount(), expected) 

        invalid = UsdGeom.Mesh(Usd.Prim())
        self.assertFalse(invalid)
        with self.assertRaises(RuntimeError):
            self.assertEqual(invalid.GetFaceCount(), 0)
        with self.assertRaises(RuntimeError):
            self.assertEqual(invalid.GetFaceCount(
                Usd.TimeCode.EarliestTime()), 0)


if __name__ == '__main__':
    unittest.main()
