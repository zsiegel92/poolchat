import contextlib
import os
from werkzeug.routing import BaseConverter

class KwargConverter(BaseConverter):

	def to_python(self, value):
		return int(value.split('=')[1])

	def to_url(self, values):
		return '='.join(BaseConverter.to_url(value)
						for value in values)


@contextlib.contextmanager
def modified_environ(*remove, **update):
	env = os.environ
	update = update or {}
	remove = remove or []

	# List of environment variables being updated or removed.
	stomped = (set(update.keys()) | set(remove)) & set(env.keys())
	# Environment variables and values to restore on exit.
	update_after = {k: env[k] for k in stomped}
	# Environment variables and values to remove on exit.
	remove_after = frozenset(k for k in update if k not in env)

	try:
		env.update(update)
		[env.pop(k, None) for k in remove]
		yield
	finally:
		env.update(update_after)
		[env.pop(k) for k in remove_after]
