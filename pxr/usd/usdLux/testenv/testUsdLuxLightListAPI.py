#!/pxrpythonsubst
#
# Copyright 2017 Pixar
#
# Licensed under the terms set forth in the LICENSE.txt file available at
# https://openusd.org/license.

from pxr import Usd, UsdGeom, UsdLux, Vt, Sdf
import unittest


class TestUsdLuxListAPI(unittest.TestCase):
    def test_ListAPI(self):
        self._test( Usd.Stage.Open('root.usda',
            Usd.Stage.LoadNone) )
    def test_ListAPI(self):
        self._test( Usd.Stage.Open('root_with_instances.usda',
            Usd.Stage.LoadNone) )

    def _test(self, stage):
        listAPI = UsdLux.LightListAPI(stage.GetPrimAtPath('/World'))
        consult = UsdLux.LightListAPI.ComputeModeConsultModelHierarchyCache
        ignore = UsdLux.LightListAPI.ComputeModeIgnoreCache

        # no cache initially
        self.assertEqual(len(listAPI.GetLightListRel().GetTargets()), 0)
        # compute w/o cache should find 1 light outside payload
        computed_list = listAPI.ComputeLightList(ignore)
        self.assertEqual(len(computed_list), 1)
        self.assertTrue(Sdf.Path('/World/Lights/Sky_light') in computed_list)
        # compute w/ cache should find 1 extra light, since 1 light
        # inside a payload has been published to cache
        computed_list = listAPI.ComputeLightList(consult)
        self.assertEqual(len(computed_list), 2)
        self.assertTrue(Sdf.Path('/World/Lights/Sky_light') in computed_list)
        self.assertTrue(Sdf.Path('/World/Geo/torch_2/light') in computed_list)

        # load payloads to discover the rest of the lights
        stage.Load()
        # if we consult the cache we still won't see lights below model
        # hierarchy
        computed_list = listAPI.ComputeLightList(consult)
        self.assertEqual(len(computed_list), 2)
        self.assertTrue(Sdf.Path('/World/Lights/Sky_light') in computed_list)
        self.assertTrue(Sdf.Path('/World/Geo/torch_2/light') in computed_list)
        # but if we ignore cache we now see 3 lights
        computed_list = listAPI.ComputeLightList(ignore)
        self.assertEqual(len(computed_list), 3)
        self.assertTrue(Sdf.Path('/World/Lights/Sky_light') in computed_list)
        self.assertTrue(Sdf.Path('/World/Geo/torch_1/light') in computed_list)
        self.assertTrue(Sdf.Path('/World/Geo/torch_2/light') in computed_list)

        # store this full list in the light list
        listAPI.StoreLightList(computed_list)

        # now using the cache should return everything
        computed_list = listAPI.ComputeLightList(consult)
        self.assertEqual(len(computed_list), 3)
        self.assertTrue(Sdf.Path('/World/Lights/Sky_light') in computed_list)
        self.assertTrue(Sdf.Path('/World/Geo/torch_1/light') in computed_list)
        self.assertTrue(Sdf.Path('/World/Geo/torch_2/light') in computed_list)

        # deactivate 1 torch model
        torch_1 = stage.GetPrimAtPath('/World/Geo/torch_1')
        torch_1.SetActive(False)

        # if we ignore the cache(s) we do see only 2 lights
        self.assertEqual(len(listAPI.ComputeLightList(ignore)), 2)
        # but the cache should continue to report 3 lights
        self.assertEqual(len(listAPI.ComputeLightList(consult)), 3)
        # invalidating the cache should cause it to report 2 lights
        listAPI.InvalidateLightList()
        self.assertEqual(len(listAPI.ComputeLightList(consult)), 2)

        # add a light filter, and confirm that it gets included as a light
        self.assertEqual(len(listAPI.ComputeLightList(ignore)), 2)
        filter = UsdLux.LightFilter.Define(stage, '/World/Lights/TestFilter')
        self.assertEqual(len(listAPI.ComputeLightList(ignore)), 3)

        # add an untyped prim and apply a LightAPI. Confirm that it also gets
        # included as a light.
        self.assertEqual(len(listAPI.ComputeLightList(ignore)), 3)
        prim = stage.DefinePrim("/World/Lights/PrimWithLightAPI")
        self.assertEqual(len(listAPI.ComputeLightList(ignore)), 3)
        UsdLux.LightAPI.Apply(prim)
        self.assertEqual(len(listAPI.ComputeLightList(ignore)), 4)

        # discard changes
        stage.Reload()

if __name__ == "__main__":
    unittest.main()
