import os
import re

src_api = r"c:\Users\shres\Desktop\zorvyn_system_design\src\api"
src_controllers = r"c:\Users\shres\Desktop\zorvyn_system_design\src\controllers"
src_routes = r"c:\Users\shres\Desktop\zorvyn_system_design\src\routes"

os.makedirs(src_controllers, exist_ok=True)
os.makedirs(src_routes, exist_ok=True)

for filename in os.listdir(src_api):
    if not filename.endswith('.py'): continue
    if filename in ('__init__.py', 'routes.py'): continue
    
    filepath = os.path.join(src_api, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    module_name = filename[:-3]
    
    # We will extract decorators and create a routes file
    # Regex to find @router.<method>("<path>", ...)
    # Wait, simple parsing:
    lines = content.split('\n')
    
    controller_lines = []
    routes_setup = [
        "from fastapi import APIRouter",
        f"from src.controllers.{module_name}_controller import *",
        "",
        "router = APIRouter()",
        ""
    ]
    
    accumulating_decorator = False
    current_decorator = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('@router.') or line.startswith('@limiter.'):
            # This line belongs to routing
            # We must capture it
            if line.startswith('@router.'):
                # We need to find the function name that follows this decorator block
                # to do router.add_api_route or replace it with add_api_route later.
                # Actually, an easier way is to just use router.add_api_route in the routes file.
                pass
                
        # Wait, parsing python code textually to split decorators from functions is incredibly brittle.
        # It's much simpler to just keep them as controller/routes merged for now.
        i += 1

print("Parsing via python is risky. Going to use a different approach.")
