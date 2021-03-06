import pytest
from numpy import array, identity, cos, sin, pi, concatenate
import requests
from tempfile import TemporaryFile


@pytest.fixture(scope='package')
def sample_file():
    tf = TemporaryFile()  # temp file to store data
    # pull the data from the web
    data = requests.get('https://www.uvm.edu/~rsmcginn/download/sample_data.h5')
    tf.write(data.content)
    data.close()  # close off the connection

    yield tf
    tf.close()  # on teardown close the tempfile


@pytest.fixture
def pelvis_af():
    return array([-0.81886302,  0.18082344, 0.54476256]), array([-0.48946473, -0.71571412, -0.49817424]),\
           array([0.29981268, -0.67457852, 0.67457852])


@pytest.fixture
def left_thigh_af():
    return array([0.03280552, 0.51524739, 0.65611038]), array([-0.99875234, 0, 0.04993762]), \
           array([0.0308188, -0.78684867, 0.61637601])


@pytest.fixture
def right_thigh_af():
    return array([-0.22030363, 0.56599008, 0.50842072]), array([-0.96024973, -0.22331389, -0.16748542]),\
           array([0.02366255, -0.66295973, 0.74828102])


@pytest.fixture
def F():
    return array([0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.0, -0.5, -0.4, -0.35, -0.45, -0.8])


@pytest.fixture(params=[2, 4])
def derivative_result(request):
    if request.param == 2:
        res = array([1.0, 1.0, 1.0, 0.5, -0.5, -2.0, -4.0, -2.0, 0.75, -0.25, -2.25, -4.75])
    elif request.param == 4:
        res = array([1.25, 0.41666667, 1.75, 1.08333333, -0.41666667, -2.75, -5.33333333, -2.70833333, 0.625,
                    -1.41666667, -0.70833333, -5.08333333])
    return request.param, res


@pytest.fixture(scope='module')
def q1n():
    return array([0.5, 0.5, 0.5, 0.5])


@pytest.fixture(scope='module')
def q2n():
    return array([0.26, 0.13, 0.64, -0.71])


@pytest.fixture(scope='module')
def q3n():
    return array([0.77, 0.46, 0.10, 0.43])


@pytest.fixture(scope='module')
def q4_2d():
    return array([[1, 0, 0, 0], [0.26, 0.13, 0.64, -0.71]])


@pytest.fixture(params=['12', '13', '23'])
def qmult(request, q1n, q2n, q3n):
    if request.param == '12':
        res = array([0.1, -0.48, 0.87, 0.03])
        return q1n, q2n, res
    elif request.param == '13':
        res = array([-0.11, 0.78, 0.45, 0.42])
        return q1n, q3n, res
    elif request.param == '23':
        res = array([0.3817, 0.5659, 0.1363, -0.7163])
        return q2n, q3n, res


@pytest.fixture(params=['1', '2', '3', '4'])
def qconj(request, q1n, q2n, q3n, q4_2d):
    if request.param == '1':
        return q1n, array([0.5, -0.5, -0.5, -0.5])
    elif request.param == '2':
        return q2n, array([0.26, -0.13, -0.64, 0.71])
    elif request.param == '3':
        return q3n, array([0.77, -0.46, -0.10, -0.43])
    elif request.param == '4':
        return q4_2d, array([[1, 0, 0, 0], [0.26, -0.13, -0.64, 0.71]])


@pytest.fixture(params=['1', '2', '3'])
def qinv(request, q1n, q2n, q3n):
    if request.param == '1':
        return q1n
    elif request.param == '2':
        return q2n
    elif request.param == '3':
        return q3n


@pytest.fixture(params=['1', '2', '3', '4'])
def q2mat(request, q1n, q2n, q3n, q4_2d):
    if request.param == '1':
        return q1n, array([[0.0,  0.0,  1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    elif request.param == '2':
        return q2n, array([[-0.8257546, 0.53511774, 0.14806656], [-0.2026174, -0.04106178, -0.97552084],
                           [-0.51693413, -0.84044258, 0.14776805]])
    elif request.param == '3':
        return q3n, array([[0.61031696, -0.57002891, 0.5494351], [0.75397371, 0.20723794, -0.62221325],
                           [0.24152751, 0.79416164, 0.55693298]])
    elif request.param == '4':
        return q4_2d, array([identity(3), [[-0.8257546, 0.53511774, 0.14806656],
                                           [-0.2026174, -0.04106178, -0.97552084],
                                           [-0.51693413, -0.84044258, 0.14776805]]])


@pytest.fixture
def R():
    r1 = array([[1, 0, 0], [0, 0, 1], [0, 1, 0]]).reshape((-1, 3, 3))

    t2 = 5 * pi / 180
    r2 = r1 @ array([[1, 0, 0], [0, cos(t2), -sin(t2)], [0, sin(t2), cos(t2)]]).reshape((-1, 3, 3))

    t3 = 7.5 * pi / 180
    r3 = r1 @ array([[1, 0, 0], [0, cos(t3), -sin(t3)], [0, sin(t2), cos(t3)]]).reshape((-1, 3, 3))

    return concatenate((r1, r2, r3), axis=0)
