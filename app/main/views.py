from . import main
from ..models import *


@main.route('/')
def index():
    return 'poe'

