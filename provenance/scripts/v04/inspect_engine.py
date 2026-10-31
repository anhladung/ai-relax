import bpy
print('CYCLES DEVICES')
try:
 p=bpy.context.preferences.addons['cycles'].preferences
 for backend in ['HIP','ONEAPI','CUDA','OPTIX']:
  try:
   p.compute_device_type=backend; p.get_devices(); print(backend,[(d.name,d.type) for d in p.devices])
  except Exception as e: print(backend,str(e)[:100])
except Exception as e: print(e)
print('PROBES',[(i.identifier) for i in bpy.types.LightProbe.bl_rna.properties['type'].enum_items])
print('EEVEE',[(p.identifier) for p in bpy.context.scene.eevee.bl_rna.properties if any(x in p.identifier for x in ['ray','trace','resolution'])])
