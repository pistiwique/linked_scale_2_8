# -*- coding:utf-8 -*-

# Blender ASSET MANAGEMENT Add-on
# Copyright (C) 2018 Legigan Jeremy AKA Pistiwique
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# <pep8 compliant>

bl_info = {
    "name": "Linked Scale",
    "description": "",
    "author": "Jeremy Legigan AKA Pistiwique",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Object"}

import bpy

from bpy.types import (
    PropertyGroup,
    Panel
    )

from bpy.props import (
    FloatProperty,
    EnumProperty,
    PointerProperty
    )


def get_constraint_axis(axis):
    sfp = bpy.context.window_manager.sfp_props
    multi_constraint = {'ALL': (True, True, True),
                        'X_Y': (True, True, False),
                        'X_Z': (True, False, True),
                        'Y_Z': (False, True, True),
                        }

    single_constraint = {0: (True, False, False),
                         1: (False, True, False),
                         2: (False, False, True),
                         }

    if sfp.linked_axis != 'FREE':
        if (axis == 0 and sfp.linked_axis not in {'ALL', 'X_Y', 'X_Z'}) or \
           (axis == 1 and sfp.linked_axis not in {'ALL', 'X_Y', 'Y_Z'}) or \
           (axis == 2 and sfp.linked_axis not in {'ALL', 'X_Z', 'Y_Z'}):
            return single_constraint[axis]

        return multi_constraint[sfp.linked_axis]

    return single_constraint[axis]


def update_axis(axis_idx, ratio):
    constraint_axis = get_constraint_axis(axis_idx)

    bpy.ops.transform.resize(
            value=(ratio, ratio, ratio),
            constraint_axis=constraint_axis,
            constraint_orientation=bpy.context.scene.transform_orientation_slots[0].type
            )

def get_dimensions(axis):
    def getter(self):
        return bpy.context.object.dimensions[int(axis)]

    return getter

def set_dimensions(axis):
    def setter(self, value):

        axis_dict = {0: self.dim_x,
                     1: self.dim_y,
                     2: self.dim_z
                     }

        convert_unit = {'METERS': 1,
                        'CENTIMETERS': 0.01,
                        'MILLIMETERS': 0.001
                        }

        unit_settings = bpy.context.scene.unit_settings
        if unit_settings.system == 'METRIC':
            factor = 1 / convert_unit[self.draw_units] * unit_settings.scale_length
        else:
            factor = 1

        update_axis(int(axis), max(0.000001, value) / axis_dict[int(axis)] / factor)

        return None

    return setter

#  -------------  COLLECTION PROPERTY -------------  #

class ScaleFromLengthProperties(PropertyGroup):
    draw_units: EnumProperty(
            name="Display_units",
            items=(('METERS', "Meters", ""),
                   ('CENTIMETERS', "Centimeters", ""),
                   ('MILLIMETERS', "Millimeters", "")
                   ),
            default='METERS'
            )

    dim_x: FloatProperty(
            name="Dimension X",
            description="Absolute bounding box of the object",
            soft_min=0.000001,
            precision=3,
            get=get_dimensions("0"),
            set=set_dimensions("0"),
            unit='LENGTH',
            )

    dim_y: FloatProperty(
            name="Dimension Y",
            description="Absolute bounding box of the object",
            soft_min=0.000001,
            precision=3,
            get=get_dimensions("1"),
            set=set_dimensions("1"),
            unit='LENGTH',
            )

    dim_z: FloatProperty(
            name="Dimension Z",
            description="Absolute bounding box of the object",
            soft_min=0.000001,
            precision=3,
            get=get_dimensions("2"),
            set=set_dimensions("2"),
            unit='LENGTH',
            )

    linked_axis: EnumProperty(
            name="Linked axis",
            items=(('ALL', "All", ""),
                   ('X_Y', "X-Y", ""),
                   ('X_Z', "X-Z", ""),
                   ('Y_Z', "Y-Z", ""),
                   ('FREE', "Free", "")),
            default='ALL',
            )


#  ----------------  PANEL  ----------------  #

class VIEW3D_PT_view3d_linked_scale(Panel):
    bl_label = "Linked Scale"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.mode == "OBJECT")


    def draw(self, context):
        unit_settings = bpy.context.scene.unit_settings

        layout = self.layout
        sfp = context.window_manager.sfp_props
        layout.prop(sfp, 'linked_axis', expand=True)
        if unit_settings.system == 'METRIC':
            layout.label(text="Given dimensions in:")
            row = layout.row(align=True)
            split = row.split(factor=0.3)
            split.separator()
            split.prop(sfp, 'draw_units', text="")
        col = layout.column(align=True)
        col.prop(sfp, 'dim_x', text="X")
        col.prop(sfp, 'dim_y', text="Y")
        col.prop(sfp, 'dim_z', text="Z")


#  --------------  REGISTER  --------------  #

CLASSES = [
    ScaleFromLengthProperties,
    VIEW3D_PT_view3d_linked_scale
    ]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.sfp_props = PointerProperty(
        type=ScaleFromLengthProperties)


def unregister():
    del bpy.types.WindowManager.sfp_props

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()