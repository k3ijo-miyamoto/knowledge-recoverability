"""Independent closed-form oracle from the adopted mathematical worksheet."""

from fractions import Fraction


def expected(params, rule):
    if set(params) != {'h', 'c', 't', 'f'} or any(type(x) is not Fraction or not 0 <= x <= 1 for x in params.values()):
        raise ValueError('Exact probability parameters required')
    h, c, t, f = (params[k] for k in ('h', 'c', 't', 'f'))
    zero = Fraction(0)
    v = c * t + (1 - c) * f
    false_pass = (1 - c) * f
    if rule == 'pi_0':
        return dict(global_unsafe=h, expected_W=zero, pub_new=zero,
                    retained_valid_old=1-h, history_risk={'NO_QUERY': h},
                    history_mass={'NO_QUERY': Fraction(1)}, publication_risk=None)
    if rule not in ('pi_R', 'pi_Q'):
        raise ValueError('Unapproved rule')
    unsafe = false_pass + (1-v)*h if rule == 'pi_R' else false_pass
    retention = (1-v)*(1-h) if rule == 'pi_R' else zero
    return dict(global_unsafe=unsafe, expected_W=c*t, pub_new=v,
                retained_valid_old=retention,
                history_risk={'PASS': false_pass/v if v else None,
                              'FAIL': (h if rule == 'pi_R' else zero) if v != 1 else None},
                history_mass={'PASS': v, 'FAIL': 1-v},
                publication_risk=false_pass/v if v else None)


def posterior(params, message):
    c, t, f = (params[k] for k in ('c', 't', 'f'))
    if message == 'PASS':
        numerator, denominator = c*t, c*t+(1-c)*f
    elif message == 'FAIL':
        numerator, denominator = c*(1-t), c*(1-t)+(1-c)*(1-f)
    else:
        raise ValueError('Unknown message')
    return numerator/denominator if denominator else None
