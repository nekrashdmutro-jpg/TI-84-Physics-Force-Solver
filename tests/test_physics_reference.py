"""Physics model tests for the FORCES suite.

The TI-BASIC programs cannot be executed outside a calculator or an emulator,
so this module mirrors, expression for expression, the arithmetic that the
programs perform — the same `cos`/`sin` in degrees, the same branch order for
the quadrant correction, the same friction rules — and checks it against
values worked out by hand.

A failure here means the physics model is wrong. It does not prove that a
calculator ran the program; that is what the structural tests in
test_builder.py cover (tokenization and group packing).
"""

import math

# ---------------------------------------------------------------------------
# Reference model: mirrors the TI-BASIC arithmetic
# ---------------------------------------------------------------------------


def _cos(degrees):
    return math.cos(math.radians(degrees))


def _sin(degrees):
    return math.sin(math.radians(degrees))


def vector_components(vectors):
    x = sum(f * _cos(a) for f, a in vectors)
    y = sum(f * _sin(a) for f, a in vectors)
    return x, y


def resultant(vectors):
    x, y = vector_components(vectors)
    return math.sqrt(x * x + y * y), x, y


def direction(x, y):
    """Mirror of VECADD's quadrant correction (atan2 by hand)."""
    if x == 0:
        angle = 270.0
        if y > 0:
            angle = 90.0
    else:
        angle = math.degrees(math.atan(y / x))
        if x < 0:
            angle = angle + 180
        if x > 0 and y < 0:
            angle = angle + 360
    if angle >= 360:
        angle -= 360
    if angle < 0:
        angle += 360
    return angle


def reference_angle(angle):
    """Mirror of VECADD's fPart(T/90)*90 and min(U,90-U)."""
    if angle >= 360:
        angle -= 360
    quadrant_rest = (angle / 90 - math.floor(angle / 90)) * 90
    return min(quadrant_rest, 90 - quadrant_rest)


def nearest_axis(angle):
    """Mirror of VECADD's round(T/90) with 4 folded back to 0.
    TI round() goes half away from zero, hence floor(x + 0.5)."""
    index = math.floor(angle / 90 + 0.5)
    if index == 4:
        index = 0
    return {0: "east", 1: "north", 2: "west", 3: "south"}[index]


def flat_surface(mass, applied, g, state, mu_s=None, mu_k=None, direction_sign=1,
                 motion_sign=1):
    """Mirror of FLATFRC. `state`: 1 at rest, 2 constant velocity, 3 accelerating.

    `direction_sign` is the push direction (+1 right, -1 left); `motion_sign`
    is the direction the object is actually moving (+1 same way as the push,
    -1 opposite). Kinetic friction always opposes `motion_sign`.
    """
    weight = mass * g
    normal = weight
    fs_max = None if mu_s is None else mu_s * normal
    fk = None if mu_k is None else mu_k * normal
    result = {
        "weight": weight,
        "normal": normal,
        "fs_max": fs_max,
        "fk": fk,
        "needs": None,
        "stays_at_rest": None,
        "net": None,
        "a": None,
        "mu_k_needed": None,
    }
    if state == 1:
        result["needs"] = abs(applied)
        if fs_max is not None:
            result["stays_at_rest"] = abs(applied) <= fs_max
    if state == 2:
        # A body at constant velocity must move along the push: friction can
        # only oppose, so motion opposite the push cannot be balanced.
        result["needs"] = abs(applied)
        result["mu_k_needed"] = abs(applied) / normal
        if fk is not None:
            result["consistent"] = abs(fk - abs(applied)) <= 0.05
    if state == 3:
        if fk is not None:
            result["net"] = (abs(applied) - motion_sign * fk) * direction_sign
            result["a"] = result["net"] / mass
    return result


def angled(mass, applied, g, angle, up, mu_s=None, mu_k=None, direction_sign=1,
           motion_sign=1):
    """Mirror of ANGPULL's analysis branch. `up`: True for a pull, False for a push."""
    u = 1 if up else -1
    weight = mass * g
    horizontal = applied * _cos(angle)
    vertical = u * applied * _sin(angle)
    normal = weight - vertical
    result = {
        "weight": weight,
        "fx": horizontal,
        "fy": vertical,
        "normal": normal,
        "leaves_surface": normal <= 0,
        "fs_max": None,
        "fk": None,
        "net": None,
        "a": None,
    }
    if result["leaves_surface"]:
        # ANGPULL: no friction is computed from a non-positive normal force
        result["a"] = direction_sign * horizontal / mass
        return result
    if mu_s is not None:
        result["fs_max"] = mu_s * normal
    if mu_k is not None:
        result["fk"] = mu_k * normal
        result["net"] = (horizontal - motion_sign * result["fk"]) * direction_sign
        result["a"] = result["net"] / mass
    return result


def angled_force_for_equilibrium(mass, g, angle, up, mu):
    """Mirror of ANGPULL's solve-for-F branch. Returns None when impossible."""
    u = 1 if up else -1
    weight = mass * g
    denominator = _cos(angle) + u * mu * _sin(angle)
    if denominator <= 0:
        return None
    force = mu * weight / denominator
    normal = weight - u * force * _sin(angle)
    if normal <= 0:
        return None
    return force, normal


def ramp(mass, g, angle, applied, up_ramp, state, mu_s=None, mu_k=None, moving_up=True):
    """Mirror of RAMPSLV. `state`: 1 at rest, 2/3 moving."""
    u = 1 if up_ramp else -1
    r = 1 if moving_up else -1
    weight = mass * g
    along = weight * _sin(angle)
    into = weight * _cos(angle)
    normal = into
    fs_max = None if mu_s is None else mu_s * normal
    fk = None if mu_k is None else mu_k * normal
    result = {
        "weight": weight,
        "along": along,
        "into": into,
        "normal": normal,
        "fs_max": fs_max,
        "fk": fk,
        "tendency": None,
        "fs_needed": None,
        "stays_at_rest": None,
        "net": None,
        "a": None,
        "critical_angle": None if mu_s is None else math.degrees(math.atan(mu_s)),
    }
    if state == 1:
        base = applied * u - along
        result["tendency"] = "up" if base > 0 else ("down" if base < 0 else "none")
        result["fs_needed"] = abs(base)
        if fs_max is not None:
            result["stays_at_rest"] = abs(base) <= fs_max
    else:
        if fk is not None:
            result["net"] = applied * u - along - r * fk
            result["a"] = result["net"] / mass
    return result


# ---------------------------------------------------------------------------
# Vector addition
# ---------------------------------------------------------------------------


def test_perpendicular_vectors():
    magnitude, x, y = resultant([(30, 0), (40, 90)])
    assert magnitude == pytest_approx(50.0)
    assert direction(x, y) == pytest_approx(53.13, abs=0.01)


def test_opposite_vectors_cancel():
    magnitude, x, y = resultant([(10, 0), (10, 180)])
    assert magnitude == pytest_approx(0.0, abs=1e-9)


def test_quadrant_two():
    magnitude, x, y = resultant([(5, 90), (5, 180)])
    assert magnitude == pytest_approx(7.0711, abs=0.001)
    assert direction(x, y) == pytest_approx(135.0)


def test_quadrant_three():
    magnitude, x, y = resultant([(4, 180), (3, 270)])
    assert magnitude == pytest_approx(5.0)
    assert direction(x, y) == pytest_approx(216.87, abs=0.01)
    assert reference_angle(direction(x, y)) == pytest_approx(36.87, abs=0.01)
    assert nearest_axis(direction(x, y)) == "west"


def test_quadrant_four():
    magnitude, x, y = resultant([(4, 0), (3, 270)])
    assert magnitude == pytest_approx(5.0)
    assert direction(x, y) == pytest_approx(323.13, abs=0.01)
    assert reference_angle(direction(x, y)) == pytest_approx(36.87, abs=0.01)
    assert nearest_axis(direction(x, y)) == "east"


def test_direction_on_the_axes():
    assert direction(5, 0) == pytest_approx(0.0)
    assert direction(0, 5) == pytest_approx(90.0)
    assert direction(-5, 0) == pytest_approx(180.0)
    assert direction(0, -5) == pytest_approx(270.0)


def test_equilibrant_is_opposite_the_resultant():
    magnitude, x, y = resultant([(3, 0), (4, 90)])
    angle = direction(x, y)
    equilibrant = angle + 180
    if equilibrant >= 360:
        equilibrant -= 360
    assert equilibrant == pytest_approx(233.13, abs=0.01)


# ---------------------------------------------------------------------------
# Horizontal surface
# ---------------------------------------------------------------------------


def test_horizontal_static_below_maximum():
    case = flat_surface(10, 30, 9.8, 1, mu_s=0.5, mu_k=0.4)
    assert case["weight"] == pytest_approx(98.0)
    assert case["normal"] == pytest_approx(98.0)
    assert case["fs_max"] == pytest_approx(49.0)
    assert case["fk"] == pytest_approx(39.2)
    assert case["needs"] == pytest_approx(30.0)
    assert case["stays_at_rest"] is True


def test_horizontal_static_above_maximum():
    case = flat_surface(10, 60, 9.8, 1, mu_s=0.5, mu_k=0.4)
    assert case["stays_at_rest"] is False
    assert case["fs_max"] == pytest_approx(49.0)


def test_horizontal_constant_velocity_is_consistent():
    case = flat_surface(10, 39.2, 9.8, 2, mu_s=0.5, mu_k=0.4)
    assert case["mu_k_needed"] == pytest_approx(0.4)
    assert case["consistent"] is True


def test_horizontal_constant_velocity_flags_a_bad_mu():
    case = flat_surface(10, 20, 9.8, 2, mu_s=0.5, mu_k=0.4)
    assert case["mu_k_needed"] == pytest_approx(0.2041, abs=0.001)
    assert case["consistent"] is False


def test_horizontal_acceleration_with_kinetic_friction():
    case = flat_surface(10, 60, 9.8, 3, mu_s=0.5, mu_k=0.4)
    assert case["net"] == pytest_approx(20.8)
    assert case["a"] == pytest_approx(2.08)


def test_horizontal_unknown_mu_never_invents_friction():
    case = flat_surface(10, 60, 9.8, 1, mu_s=None, mu_k=None)
    assert case["fs_max"] is None
    assert case["fk"] is None
    assert case["stays_at_rest"] is None


def test_kinetic_friction_opposes_motion_not_the_push():
    with_push = flat_surface(10, 60, 9.8, 3, mu_s=0.5, mu_k=0.4, motion_sign=1)
    against_push = flat_surface(10, 60, 9.8, 3, mu_s=0.5, mu_k=0.4, motion_sign=-1)
    assert with_push["net"] == pytest_approx(20.8)
    assert against_push["net"] == pytest_approx(60 + 39.2)
    assert against_push["net"] > with_push["net"]


def test_horizontal_sliding_against_the_push_slows_down():
    # pushed right at 60 N while sliding left: both push and friction act right,
    # so the acceleration points right, opposite to the motion.
    case = flat_surface(10, 60, 9.8, 3, mu_s=0.5, mu_k=0.4,
                        direction_sign=1, motion_sign=-1)
    assert case["a"] == pytest_approx(9.92)
    assert case["a"] > 0


# ---------------------------------------------------------------------------
# Angled forces
# ---------------------------------------------------------------------------


def test_upward_pull_reduces_the_normal_force():
    case = angled(10, 50, 9.8, 30, up=True, mu_k=0.3)
    assert case["fx"] == pytest_approx(43.301, abs=0.001)
    assert case["fy"] == pytest_approx(25.0, abs=1e-9)
    assert case["normal"] == pytest_approx(73.0)
    assert case["fk"] == pytest_approx(21.9)
    assert case["net"] == pytest_approx(21.4013, abs=0.001)
    assert case["a"] == pytest_approx(2.14013, abs=0.001)


def test_downward_push_increases_the_normal_force():
    pull = angled(10, 50, 9.8, 30, up=True)
    push = angled(10, 50, 9.8, 30, up=False)
    assert push["normal"] == pytest_approx(123.0)
    assert push["normal"] > pull["normal"]


def test_object_loses_contact():
    case = angled(10, 200, 9.8, 30, up=True, mu_k=0.3)
    assert case["fy"] == pytest_approx(100.0)
    assert case["normal"] == pytest_approx(-2.0)
    assert case["leaves_surface"] is True
    assert case["fk"] is None  # friction is never computed from FN <= 0
    assert case["a"] == pytest_approx(173.205 / 10, abs=0.001)


def test_angled_equilibrium_force():
    solution = angled_force_for_equilibrium(10, 9.8, 30, up=True, mu=0.5)
    force, normal = solution
    assert force == pytest_approx(43.905, abs=0.01)
    assert normal == pytest_approx(76.048, abs=0.01)
    assert force * _cos(30) == pytest_approx(0.5 * normal, abs=0.01)


def test_angled_equilibrium_has_no_solution_when_friction_wins():
    # Pulling up can always balance: cos(T) + mu*sin(T) > 0 for T < 90.
    assert angled_force_for_equilibrium(10, 9.8, 60, up=True, mu=0.7) is not None
    # Pushing down cannot: cos(60) - 0.7*sin(60) < 0, so no finite push works.
    assert angled_force_for_equilibrium(10, 9.8, 60, up=False, mu=0.7) is None


def test_angled_acceleration_when_moving_against_the_pull():
    with_pull = angled(10, 50, 9.8, 30, up=True, mu_k=0.3, motion_sign=1)
    against_pull = angled(10, 50, 9.8, 30, up=True, mu_k=0.3, motion_sign=-1)
    assert with_pull["net"] == pytest_approx(21.4013, abs=0.001)
    assert against_pull["net"] == pytest_approx(43.3013 + 21.9, abs=0.01)
    assert against_pull["a"] == pytest_approx(6.52013, abs=0.01)


# ---------------------------------------------------------------------------
# Inclined planes
# ---------------------------------------------------------------------------


def test_ramp_components_without_friction():
    case = ramp(10, 9.8, 30, 0, up_ramp=True, state=2, moving_up=False)
    assert case["weight"] == pytest_approx(98.0)
    assert case["along"] == pytest_approx(49.0)
    assert case["into"] == pytest_approx(84.8705, abs=0.001)
    assert case["normal"] == pytest_approx(84.8705, abs=0.001)


def test_ramp_static_friction_holds():
    case = ramp(10, 9.8, 30, 0, up_ramp=True, state=1, mu_s=0.6)
    assert case["fs_max"] == pytest_approx(50.9223, abs=0.001)
    assert case["tendency"] == "down"
    assert case["fs_needed"] == pytest_approx(49.0)
    assert case["stays_at_rest"] is True
    assert case["critical_angle"] == pytest_approx(30.964, abs=0.01)


def test_ramp_static_friction_too_small():
    case = ramp(10, 9.8, 30, 0, up_ramp=True, state=1, mu_s=0.3)
    assert case["fs_max"] == pytest_approx(25.4611, abs=0.001)
    assert case["stays_at_rest"] is False


def test_ramp_kinetic_friction_down_the_slope():
    case = ramp(10, 9.8, 30, 0, up_ramp=True, state=3, moving_up=False, mu_k=0.25)
    assert case["fk"] == pytest_approx(21.2176, abs=0.001)
    assert case["net"] == pytest_approx(-27.7824, abs=0.001)
    assert case["a"] == pytest_approx(-2.77824, abs=0.001)


def test_ramp_applied_force_up_the_ramp():
    case = ramp(10, 9.8, 30, 80, up_ramp=True, state=3, moving_up=True, mu_k=0.25)
    assert case["net"] == pytest_approx(80 - 49.0 - 21.2176, abs=0.001)
    assert case["a"] > 0


def test_ramp_applied_force_down_the_ramp():
    case = ramp(10, 9.8, 30, 80, up_ramp=False, state=3, moving_up=False, mu_k=0.25)
    assert case["net"] == pytest_approx(-80 - 49.0 + 21.2176, abs=0.001)
    assert case["a"] < 0


def test_ramp_friction_direction_follows_the_tendency():
    down = ramp(10, 9.8, 30, 0, up_ramp=True, state=1, mu_s=0.6)
    up = ramp(10, 9.8, 30, 60, up_ramp=True, state=1, mu_s=0.6)
    assert down["tendency"] == "down"
    assert up["tendency"] == "up"


def test_ramp_static_mu_unknown_is_reported_not_assumed():
    case = ramp(10, 9.8, 30, 0, up_ramp=True, state=1, mu_s=None)
    assert case["stays_at_rest"] is None
    assert case["fs_needed"] == pytest_approx(49.0)


# ---------------------------------------------------------------------------
# tiny helper so the assertions read like the problem statements
# ---------------------------------------------------------------------------


class pytest_approx:
    def __new__(cls, value, abs=1e-6):  # noqa: A002 - mirrors pytest.approx
        import pytest

        return pytest.approx(value, abs=abs, rel=0)
