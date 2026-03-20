#!/usr/bin/env python3
"""
liggghts_to_blazedem.py
-----------------------
Translates a LIGGGHTS input script (sphere-only, primitive geometry) into a
BlazeDEM project directory.

Supported LIGGGHTS features:
  - units si
  - region block / cylinder z (primitive geometry only — no STL)
  - fix property/global: youngsModulus, poissonsRatio, coefficientRestitution,
                         coefficientFriction
  - pair_style gran model hertz/hooke tangential history
  - fix gravity
  - fix wall/gran primitive: zplane, zcylinder
  - fix particletemplate/sphere (single template, monodisperse)
  - fix insert/pack
  - timestep
  - run

Limitations / approximations:
  - LIGGGHTS Hertz contact is nonlinear (F ∝ δ^1.5).  BlazeDEM uses a linear
    spring-dashpot.  Kn is estimated by linearising Hertz at δ = 0.1 % of
    particle diameter — a common DEM practice.
  - Multiple atom types / particle size distributions are not supported.
  - STL mesh walls are not supported.
  - Streaming insertion (insert/stream) is not supported; particles are placed
    on a regular grid inside the domain at t=0.

Usage:
  python liggghts_to_blazedem.py in.noCohesion \
      --output /path/to/blazedem/Projects/5.noCohesion \
      --name noCohesion
"""

import argparse
import math
import os
import re
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tok(line):
    """Split a line into tokens, stripping inline comments."""
    return line.split('#')[0].split()


def parse_liggghts(path):
    """Parse a LIGGGHTS input file and return a structured dict."""
    data = {
        'units': 'si',
        'timestep': None,
        'gravity_mag': None,
        'gravity_vec': None,
        'E': None,
        'nu': None,
        'COR': None,
        'friction': None,
        'contact_model': 'hertz',
        'walls': [],           # list of {'type': 'zplane'|'zcylinder', ...}
        'particles': [],       # list of {'radius': r, 'density': rho}
        'insert_pack': None,   # {'region': ..., 'n': N}
        'regions': {},         # name -> {'type': ..., ...}
        'run_steps': 0,
    }

    with open(path) as f:
        raw_lines = f.readlines()

    # Join continuation lines (lines ending with &)
    lines = []
    buf = ''
    for raw in raw_lines:
        stripped = raw.rstrip()
        if stripped.endswith('&'):
            buf += stripped[:-1] + ' '
        else:
            buf += stripped
            lines.append(buf)
            buf = ''
    if buf:
        lines.append(buf)

    total_run = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        t = _tok(line)
        if not t:
            continue

        cmd = t[0].lower()

        if cmd == 'units':
            data['units'] = t[1].lower()

        elif cmd == 'timestep':
            data['timestep'] = float(t[1])

        elif cmd == 'region':
            rname = t[1]
            rtype = t[2].lower()
            if rtype == 'block':
                data['regions'][rname] = {
                    'type': 'block',
                    'xlo': float(t[3]), 'xhi': float(t[4]),
                    'ylo': float(t[5]), 'yhi': float(t[6]),
                    'zlo': float(t[7]), 'zhi': float(t[8]),
                }
            elif rtype == 'cylinder':
                # cylinder <dim> <c1> <c2> <radius> <lo> <hi>
                dim  = t[3]
                c1   = float(t[4])
                c2   = float(t[5])
                rad  = float(t[6])
                lo   = float(t[7])
                hi   = float(t[8])
                data['regions'][rname] = {
                    'type': 'cylinder', 'dim': dim,
                    'c1': c1, 'c2': c2, 'radius': rad, 'lo': lo, 'hi': hi,
                }

        elif cmd == 'fix':
            fix_id   = t[1]
            fix_grp  = t[2]
            fix_type = t[3].lower() if len(t) > 3 else ''

            # --- material properties ---
            if fix_type == 'property/global':
                prop = t[4].lower()
                if prop == 'youngsmodulus':
                    data['E'] = float(t[6])
                elif prop == 'poissonsratio':
                    data['nu'] = float(t[6])
                elif prop == 'coefficientrestitution':
                    # peratomtypepair 1 value
                    data['COR'] = float(t[-1])
                elif prop == 'coefficientfriction':
                    data['friction'] = float(t[-1])

            # --- gravity ---
            elif fix_type == 'gravity':
                data['gravity_mag'] = float(t[4])
                # vector follows keyword "vector"
                vi = t.index('vector') if 'vector' in t else None
                if vi:
                    data['gravity_vec'] = [float(t[vi+1]),
                                           float(t[vi+2]),
                                           float(t[vi+3])]

            # --- walls ---
            elif 'wall/gran' in fix_type or (len(t) > 4 and 'wall/gran' in ' '.join(t)):
                # Rebuild from raw line (may have continuation)
                raw_fix = line
                if 'primitive' in raw_fix:
                    # extract wall type
                    parts = raw_fix.split()
                    try:
                        prim_idx = parts.index('primitive')
                    except ValueError:
                        continue
                    wtype = parts[prim_idx + 3] if prim_idx + 3 < len(parts) else None
                    if wtype == 'zplane':
                        z = float(parts[prim_idx + 4])
                        data['walls'].append({'type': 'zplane', 'z': z})
                    elif wtype == 'zcylinder':
                        r    = float(parts[prim_idx + 4])
                        cx   = float(parts[prim_idx + 5])
                        cy   = float(parts[prim_idx + 6])
                        data['walls'].append({'type': 'zcylinder',
                                              'radius': r, 'cx': cx, 'cy': cy})

            # --- particle template ---
            elif fix_type == 'particletemplate/sphere':
                radius  = None
                density = None
                for i, tok in enumerate(t):
                    if tok == 'radius':
                        radius = float(t[i + 2])   # "radius constant VALUE"
                    if tok == 'density':
                        density = float(t[i + 2])  # "density constant VALUE"
                if radius and density:
                    data['particles'].append({'radius': radius, 'density': density})

            # --- insertion ---
            elif fix_type == 'insert/pack':
                n = None
                region_name = None
                for i, tok in enumerate(t):
                    if tok == 'particles_in_region':
                        n = int(t[i + 1])
                    if tok == 'region':
                        region_name = t[i + 1]
                data['insert_pack'] = {'region': region_name, 'n': n}

        elif cmd == 'pair_style':
            if 'hertz' in line.lower():
                data['contact_model'] = 'hertz'
            elif 'hooke' in line.lower():
                data['contact_model'] = 'hooke'

        elif cmd == 'run':
            steps = int(t[1])
            total_run = max(total_run, steps)

    data['run_steps'] = total_run
    return data


# ---------------------------------------------------------------------------
# Contact parameter conversion
# ---------------------------------------------------------------------------

def hertz_to_linear_kn(E, nu, R_eff, delta_frac=0.001):
    """
    Linearise the Hertz contact law F = (4/3)*E* sqrt(R_eff) delta^1.5
    at a characteristic overlap delta = delta_frac * 2*R_eff.

    Returns Kn in the same force/length units as E (i.e. N/m if E in Pa).
    """
    E_star = E / (2.0 * (1.0 - nu**2))
    R = R_eff  # effective radius
    d_particle = 2.0 * R_eff  # use R_eff as representative radius
    delta_c = delta_frac * d_particle
    Kn = (4.0 / 3.0) * E_star * math.sqrt(R) * math.sqrt(delta_c)
    return Kn


# ---------------------------------------------------------------------------
# Unit conversion  (SI → BlazeDEM hybrid: cm, kg, s, N)
# ---------------------------------------------------------------------------

def si_to_blaze(val, quantity):
    """Convert SI quantity to BlazeDEM units."""
    conversions = {
        'length':      100.0,        # m  → cm
        'radius':      100.0,
        'diameter':    100.0,
        'velocity':    100.0,        # m/s → cm/s
        'acceleration': 100.0,       # m/s² → cm/s²
        'density':     1e-6,         # kg/m³ → kg/cm³
        'stiffness':   0.01,         # N/m  → N/cm
        'time':        1.0,
    }
    return val * conversions[quantity]


# ---------------------------------------------------------------------------
# Grid calculation
# ---------------------------------------------------------------------------

def compute_grid(n_particles, radius_cm, domain):
    """
    Given N particles of radius r (cm) in a domain dict, return
    (nx, ny, nz, start_x, start_y, start_z, spacing) for BlazeDEM grid.
    domain keys: xlo, xhi, ylo, yhi, zlo, zhi  (cm)
    """
    spacing = 2.2 * radius_cm  # 10% gap

    # Fit a cube-ish grid
    nx = max(1, int((domain['xhi'] - domain['xlo']) / spacing))
    ny = max(1, int((domain['yhi'] - domain['ylo']) / spacing))
    nz = max(1, int((domain['zhi'] - domain['zlo']) / spacing))

    # Scale down to match n_particles (keep proportions)
    total = nx * ny * nz
    if total > n_particles:
        scale = (n_particles / total) ** (1.0 / 3.0)
        nx = max(1, round(nx * scale))
        ny = max(1, round(ny * scale))
        nz = max(1, int(math.ceil(n_particles / (nx * ny))))

    # Centre in domain
    lx = nx * spacing
    ly = ny * spacing
    lz = nz * spacing
    sx = (domain['xlo'] + domain['xhi']) / 2.0 - lx / 2.0 + radius_cm
    sy = (domain['ylo'] + domain['yhi']) / 2.0 - ly / 2.0 + radius_cm
    sz = domain['zlo'] + radius_cm + spacing

    return nx, ny, nz, sx, sy, sz, spacing


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

def write_wobj_cylinder(path, radius_cm, height_cm, cx_cm, cy_cm,
                        z_lo_cm, z_hi_cm):
    """
    Write a .WOBJ for a vertical zcylinder with top and bottom caps.

    BlazeDEM cylinder WOBJ format (matches BallMill drum convention):
      - NUM_SURFACES: 1 with index -1
      - Top: true / Bot: true  →  BlazeDEM adds cap collision internally
      - normalT: 0 0 -1  (top cap normal pointing inward = -Z)
      - normalB: 0 0  1  (bottom cap normal pointing inward = +Z)
      - Offset: (cx - r, cy - r, z_lo)
          because center_bot_cap = Offset + r*(1,1,1 - normalB)
                                 = Offset + r*(1,1,0)
          setting Offset = (cx-r, cy-r, z_lo) gives center_bot_cap = (cx, cy, z_lo)
    """
    name = os.path.splitext(os.path.basename(path))[0]
    # Offset such that bottom cap centre = (cx, cy, z_lo)
    off_x = cx_cm - radius_cm
    off_y = cy_cm - radius_cm
    off_z = z_lo_cm

    with open(path, 'w') as f:
        f.write(f'Title: "{name}"\n')
        f.write(f'Descp: "Vertical_cylinder_with_caps"\n\n')
        f.write('Geometry-Specfications\n\n')
        f.write('NUM_VERTEX: 0\n\n')
        f.write('NUM_SURFACES: 1\n\n')
        f.write(f'-1 "Barrel"\n')
        f.write(f'Diameter: {2.0 * radius_cm:.6f}\n')
        f.write(f'Height:   {height_cm:.6f}\n')
        f.write(f'Top:      true\n')
        f.write(f'Bot:      true\n')
        f.write(f'normalT:  0.0 0.0 -1.0\n')
        f.write(f'normalB:  0.0 0.0  1.0\n')
        f.write(f'Offset:   {off_x:.6f} {off_y:.6f} {off_z:.6f}\n')


def write_pobj(path, name, diameter_cm, density_kgcm3,
               kn_pp, cor_pp, fric_pp,
               kn_ps, cor_ps, fric_ps):
    with open(path, 'w') as f:
        f.write(f'Title: "{name}"\n')
        f.write(f'Descp: "Generated_by_liggghts_to_blazedem"\n\n')
        f.write('Geometry_Specfications \n\n')
        f.write(f'Diameter: {diameter_cm:.6f}\n')
        f.write(f'Density:  {density_kgcm3:.8f}\n\n\n')

        for section, kn, cor, fric in [
            ('Particle_Particle', kn_pp, cor_pp, fric_pp),
            ('Particle_Surface',  kn_ps, cor_ps, fric_ps),
            ('Particle_Lifter',   kn_ps, cor_ps, fric_ps),
        ]:
            f.write(f'{section}\n\n')
            f.write(f'COR:              {cor:.4f}\n')
            f.write(f'Kn(N/cm):         {kn:.4f}\n')
            f.write(f'Static_Friction:  {fric:.4f}\n')
            f.write(f'Kinetic_Friction: {fric:.4f}\n\n\n')


def write_world(path, project_name, world_name,
                wobj_name, pobj_name, n_particles,
                timestep, gravity_xyz_cms2,
                origin_cm, world_size_cm, cell_size_cm,
                nx, ny, nz, start_xyz_cm, spacing_cm,
                total_time_s, output_every_steps):
    with open(path, 'w') as f:
        gx, gy, gz = gravity_xyz_cms2
        ox, oy, oz = origin_cm
        wx, wy, wz = world_size_cm
        cs = cell_size_cm
        sx, sy, sz = start_xyz_cm

        f.write(f'Title: "{project_name}"\n')
        f.write('ModelType(Specfic|0:TC_COR|1:KN_COR):     1\n')
        f.write('Simulation_Type(0=General,1=mill,2=silo): 0\n')
        f.write('Particle_Type(0=sphere,1=poly,2=mixed):   0\n')
        f.write(f'Delta_t(s):       {timestep:.2E}\n')
        f.write('\n')
        f.write('_________________________________________________\n')
        f.write('             1_Geometrical-Information\n\n\n')
        f.write('---------------------------------------\n')
        f.write(' 1.1_Surface_Objects_(index__name)\n')
        f.write('---------------------------------------\n')
        f.write('Number: 1\n\n')
        f.write(f'1 {wobj_name}\n\n')
        f.write('---------------------------------------\n')
        f.write(' 1.2_Particle_Objects_(index__name__number)\n')
        f.write('---------------------------------------\n')
        f.write('Number: 1\n\n')
        f.write(f'1 {pobj_name} {n_particles}\n\n')
        f.write('---------------------------------------\n')
        f.write(' 1.3_Volume_Objects_(index__name)\n')
        f.write('---------------------------------------\n\n')
        f.write('Number: 0 Repeat: 0\n\n')
        f.write('_________________________________________________\n\n\n\n')
        f.write('_________________________________________________\n')
        f.write('             2_Simulation_Setup\n\n')
        f.write(f'Num_Particles:    {n_particles}\n')
        f.write(f'ForceField(cm/s): {gx:.6f}  {gy:.6f}  {gz:.6f}\n\n')
        f.write('---------------------------------------------\n')
        f.write('Rotation:         1\n')
        f.write('RollRes:          0.000\n')
        f.write('GlobalDamp:       1.0\n')
        f.write('VelLimit:         0.000\n')
        f.write('_________________________________________________\n\n\n\n')
        f.write('_________________________________________________\n')
        f.write('            3_Spatial-Grid-Computation\n\n')
        f.write(f'Origin:       {ox:.4f}   {oy:.4f}  {oz:.4f}\n')
        f.write(f'World_Size:   {wx:.4f}  {wy:.4f}  {wz:.4f}\n')
        f.write(f'Cell_Size:    {cs:.4f}  {cs:.4f}  {cs:.4f}\n')
        f.write('_________________________________________________\n\n\n')
        f.write('_________________________________________________\n')
        f.write('            4_Inital_Particle-Setup\n\n')
        f.write('Read_FromFile: 0\n')
        f.write('GridType(1=ran): 0\n')
        f.write(f'GridSize(X,Y,Z): {nx}  {ny}  {nz}\n')
        f.write(f'Start(X,Y,Z):    {sx:.4f}  {sy:.4f}  {sz:.4f}\n')
        f.write(f'Space:           {spacing_cm:.4f}  {spacing_cm:.4f}  {spacing_cm:.4f}\n')
        f.write('Velocity:        0.0000  0.0000  0.0000\n\n\n')
        f.write('_________________________________________________\n\n\n\n')
        f.write('_________________________________________________\n')
        f.write('             5_Output_Options\n\n')
        f.write('Display:           1 1 0.50\n')
        f.write('View:              0\n')
        f.write('FPS:               30\n')
        f.write('GL_DEBUG           0\n')
        f.write(f'File_write(0=none) {output_every_steps}\n')
        f.write(f'total_Time:        {total_time_s:.4f}\n')
        f.write('time_limit:        0\n')
        f.write(f'energy_diss:       {output_every_steps}\n')
        f.write('wall_forces:       0\n')
        f.write('_______________________________________________\n\n\n')
        f.write('_________________________________________________\n')
        f.write('          6_Simulation_Specfic_Options\n\n')
        f.write('Hatch_mode:        0\n')
        f.write('Flow_counter:      0\n')
        f.write('kill_after:        0\n')
        f.write('_________________________________________________\n\n')
        f.write('#END OF INPUT\n')


# ---------------------------------------------------------------------------
# Main translator
# ---------------------------------------------------------------------------

def translate(liggghts_input, output_dir, project_name, world_name):
    print(f"[liggghts_to_blazedem] Parsing: {liggghts_input}")
    d = parse_liggghts(liggghts_input)

    # --- Validate ---
    missing = [k for k in ('timestep', 'E', 'nu', 'COR', 'friction',
                            'gravity_mag', 'gravity_vec') if d[k] is None]
    if missing:
        sys.exit(f"ERROR: Could not parse required fields: {missing}")
    if not d['particles']:
        sys.exit("ERROR: No particle template found.")

    # Use first particle template only
    p = d['particles'][0]
    R_m   = p['radius']       # metres
    rho_m = p['density']      # kg/m³
    n_particles = (d['insert_pack'] or {}).get('n', 250)

    # --- Unit conversions ---
    dt         = d['timestep']                              # s (same)
    R_cm       = si_to_blaze(R_m, 'radius')
    D_cm       = 2.0 * R_cm
    rho_cm     = si_to_blaze(rho_m, 'density')             # kg/cm³
    g_vec_cms2 = [v * si_to_blaze(d['gravity_mag'], 'acceleration')
                  for v in d['gravity_vec']]

    # --- Contact parameters ---
    # Particle-particle: R_eff = R/2
    kn_pp_Nm = hertz_to_linear_kn(d['E'], d['nu'], R_m / 2.0)
    kn_pp    = si_to_blaze(kn_pp_Nm, 'stiffness')          # N/cm

    # Particle-surface: R_eff = R
    kn_ps_Nm = hertz_to_linear_kn(d['E'], d['nu'], R_m)
    kn_ps    = si_to_blaze(kn_ps_Nm, 'stiffness')          # N/cm

    # --- Geometry ---
    # Find cylinder wall
    cyl = next((w for w in d['walls'] if w['type'] == 'zcylinder'), None)
    zplanes = sorted([w['z'] for w in d['walls'] if w['type'] == 'zplane'])

    if cyl is None:
        sys.exit("ERROR: No zcylinder wall found — only cylinder geometry is "
                 "currently supported.")
    if len(zplanes) < 2:
        sys.exit("ERROR: Need at least two zplane walls (bottom + top).")

    cyl_r_cm = si_to_blaze(cyl['radius'], 'length')
    cyl_cx   = si_to_blaze(cyl['cx'], 'length')
    cyl_cy   = si_to_blaze(cyl['cy'], 'length')
    z_lo_cm  = si_to_blaze(zplanes[0], 'length')
    z_hi_cm  = si_to_blaze(zplanes[-1], 'length')
    height_cm = z_hi_cm - z_lo_cm

    # Grid domain (box inscribed in cylinder)
    s = cyl_r_cm * math.sqrt(2.0) / 2.0  # half-side of inscribed square
    domain = {
        'xlo': cyl_cx - s, 'xhi': cyl_cx + s,
        'ylo': cyl_cy - s, 'yhi': cyl_cy + s,
        'zlo': z_lo_cm,    'zhi': z_hi_cm,
    }
    nx, ny, nz, sx, sy, sz, sp = compute_grid(n_particles, R_cm, domain)
    actual_n = nx * ny * nz

    # Spatial grid params
    margin = R_cm * 2.0
    ox = cyl_cx - cyl_r_cm - margin
    oy = cyl_cy - cyl_r_cm - margin
    oz = z_lo_cm - margin
    wx = 2.0 * (cyl_r_cm + margin)
    wy = wx
    wz = height_cm + 2.0 * margin
    cell_size = round(D_cm * 2.0, 2)  # cells = 2x diameter (safe NN search)

    # Simulation time
    total_time = d['run_steps'] * dt

    # Output frequency (match LIGGGHTS thermo interval of 1000 steps)
    output_every = 1000

    # --- Create output directories ---
    dirs = {
        'world':  os.path.join(output_dir, 'World'),
        'pobj':   os.path.join(output_dir, 'ParticleObjects'),
        'wobj':   os.path.join(output_dir, 'SurfaceObjects'),
        'vobj':   os.path.join(output_dir, 'VolumeObjects'),
    }
    for d_ in dirs.values():
        os.makedirs(d_, exist_ok=True)

    wobj_name = 'Cylinder'
    pobj_name = 'Sphere'

    # --- Write files ---
    write_wobj_cylinder(
        os.path.join(dirs['wobj'], f'{wobj_name}.WOBJ'),
        cyl_r_cm, height_cm, cyl_cx, cyl_cy, z_lo_cm, z_hi_cm,
    )

    write_pobj(
        os.path.join(dirs['pobj'], f'{pobj_name}.POBJ'),
        pobj_name, D_cm, rho_cm,
        kn_pp, d['COR'], d['friction'],
        kn_ps, d['COR'], d['friction'],
    )

    write_world(
        os.path.join(dirs['world'], f'{world_name}.World'),
        project_name, world_name,
        wobj_name, pobj_name, actual_n,
        dt, g_vec_cms2,
        (ox, oy, oz), (wx, wy, wz), cell_size,
        nx, ny, nz, (sx, sy, sz), sp,
        total_time, output_every,
    )

    # --- Summary ---
    print()
    print("=" * 60)
    print(f"  BlazeDEM project written to: {output_dir}")
    print("=" * 60)
    print(f"  Particles:     {actual_n}  (requested {n_particles})")
    print(f"  Diameter:      {D_cm:.4f} cm  ({2*R_m*1000:.2f} mm)")
    print(f"  Density:       {rho_cm:.2e} kg/cm³  ({rho_m:.0f} kg/m³)")
    print(f"  Timestep:      {dt:.2e} s")
    print(f"  Sim time:      {total_time:.4f} s  ({d['run_steps']} steps)")
    print(f"  Cylinder:      r={cyl_r_cm:.3f} cm, h={height_cm:.3f} cm")
    print(f"  Gravity:       {g_vec_cms2} cm/s²")
    print(f"  Contact model: {d['contact_model']} → linear spring-dashpot")
    print(f"    Kn PP:       {kn_pp:.4f} N/cm  (from Hertz linearisation)")
    print(f"    Kn PS:       {kn_ps:.4f} N/cm")
    print(f"    COR:         {d['COR']}")
    print(f"    Friction:    {d['friction']}")
    print(f"  Grid:          {nx}×{ny}×{nz} = {actual_n} particles")
    print()
    print("  NOTE: BlazeDEM uses a linear spring-dashpot.  Kn is estimated")
    print("  by linearising the Hertz law at δ = 0.1% of particle diameter.")
    print("  Results will be qualitatively comparable, not exact.")
    print()

    return actual_n, world_name


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input',  help='LIGGGHTS input file (in.*)')
    ap.add_argument('--output', required=True,
                    help='Output BlazeDEM project directory')
    ap.add_argument('--name',   default='translated',
                    help='Project/world name (default: translated)')
    args = ap.parse_args()

    world_name = args.name
    translate(args.input, args.output, args.name, world_name)
