def load_at_optic(optic: str):
    if optic == 'v24':
        from .physics_based.p3_elements_v24 import ring
    elif optic == 'v24_c4l':
        from .physics_based.p3_elements_v24_c4l import ring
    else:
        raise ValueError(f"Optic {optic} is unknown.")
    return ring
