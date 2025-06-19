import subprocess

import click
from frappe.commands import pass_context
from frappe.exceptions import SiteNotSpecifiedError


@click.command(
	"run-microbenchmarks",
	context_settings=dict(
		ignore_unknown_options=True,
	),
	add_help_option=False,
)
@click.argument("benchargs", nargs=-1, type=click.UNPROCESSED)
@pass_context
def run_benchmarks(ctx, benchargs):
	import frappe

	if not ctx.sites:
		raise SiteNotSpecifiedError
	site = ctx.sites[0]
	benchargs = ("--site", site) + benchargs
	frappe.init(site)
	frappe.cache.flushall()

	from caffeine.microbenchmarks import run_benchmarks

	# XXX: We can't invoke it directly pyperf wants to be the entry point
	# Anyway, this shouldn't be a problem. It's no different than shell invoking it.
	subprocess.check_call(["../env/bin/python3", run_benchmarks.__file__, *benchargs])


@click.command("setup-loadtest-data")
@click.option("--n-items", type=int, help="Number of test items to create")
@click.option("--n-warehouses", type=int, help="Number of warehouses to create")
@click.option("--users-per-warehouse", type=int, help="Number of concurrent user for each warehouse")
@click.option("--customers-per-warehouse", type=int, help="Number of customers per warehouse")
@pass_context
def setup_loadtest(ctx, **args):
	import frappe

	from caffeine.loadtest.test_data import Setup

	if not ctx.sites:
		raise SiteNotSpecifiedError
	site = ctx.sites[0]
	try:
		frappe.init(site)
		frappe.connect()

		# remove optional arguments
		for k, v in list(args.items()):
			if v is None:
				args.pop(k)

		s = Setup(**args)
		s.setup_all()
	finally:
		frappe.destroy()


commands = [
	run_benchmarks,
	setup_loadtest,
]
