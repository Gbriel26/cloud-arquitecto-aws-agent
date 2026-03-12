"""
Script de verificación manual para formatear_respuesta
"""
from agent import formatear_respuesta, SIGNATURE

print("=" * 60)
print("VERIFICACIÓN DE formatear_respuesta")
print("=" * 60)

# Test 1: String básico
print("\n1. Test con string básico:")
result1 = formatear_respuesta("Hola mundo")
expected1 = "Hola mundo" + SIGNATURE
print(f"   Input: 'Hola mundo'")
print(f"   Output: {repr(result1)}")
print(f"   ✓ PASS" if result1 == expected1 else f"   ✗ FAIL")

# Test 2: String vacío
print("\n2. Test con string vacío:")
result2 = formatear_respuesta("")
expected2 = SIGNATURE
print(f"   Input: ''")
print(f"   Output: {repr(result2)}")
print(f"   ✓ PASS" if result2 == expected2 else f"   ✗ FAIL")

# Test 3: String multi-línea
print("\n3. Test con string multi-línea:")
input3 = "Línea 1\nLínea 2\nLínea 3"
result3 = formatear_respuesta(input3)
expected3 = input3 + SIGNATURE
print(f"   Input: 'Línea 1\\nLínea 2\\nLínea 3'")
print(f"   Output: {repr(result3)}")
print(f"   ✓ PASS" if result3 == expected3 else f"   ✗ FAIL")

# Test 4: TypeError con None
print("\n4. Test TypeError con None:")
try:
    formatear_respuesta(None)
    print("   ✗ FAIL - No se lanzó TypeError")
except TypeError as e:
    if "output_text debe ser de tipo str" in str(e):
        print(f"   ✓ PASS - TypeError lanzado correctamente: {e}")
    else:
        print(f"   ✗ FAIL - Mensaje incorrecto: {e}")

# Test 5: TypeError con int
print("\n5. Test TypeError con int:")
try:
    formatear_respuesta(123)
    print("   ✗ FAIL - No se lanzó TypeError")
except TypeError as e:
    if "output_text debe ser de tipo str" in str(e):
        print(f"   ✓ PASS - TypeError lanzado correctamente: {e}")
    else:
        print(f"   ✗ FAIL - Mensaje incorrecto: {e}")

# Test 6: TypeError con list
print("\n6. Test TypeError con list:")
try:
    formatear_respuesta(["texto"])
    print("   ✗ FAIL - No se lanzó TypeError")
except TypeError as e:
    if "output_text debe ser de tipo str" in str(e):
        print(f"   ✓ PASS - TypeError lanzado correctamente: {e}")
    else:
        print(f"   ✗ FAIL - Mensaje incorrecto: {e}")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
