### Caffeine

Frappes are usually not caffeinated enough, we want a lot of caffeine in ours.

[![Sanity Test](https://github.com/frappe/caffeine/actions/workflows/ci.yml/badge.svg?event=schedule)](https://github.com/frappe/caffeine/actions/workflows/ci.yml)

### Goal

This project has only one goal: **Speedup Frappe ecosystem by approximately by 2x.**

Approximately, this boils down to:
- Set up a good benchmark suite ranging from microbenchmarks to realistic traces.
- Optimize EVERYTHING. Every 0.1% on critical path counts.
- Make deployments resource efficient by tuning various knobs.

### Running Microbenchmarks

This project uses [pyperf](https://pyperf.readthedocs.io/) to write various micro-benchmarks. Follow these steps to run the benchmarks:
1. Install the app as usual: `bench get-app caffeine`
3. Create a fresh site that hasn't been altered: `bench new-site bench.localhost`
4. Allow running tests on this site: `bench --site bench.localhost set-config allow_tests true`
5. Run benchmarks `bench --site bench.localhost run-microbenchmarks`

Note: It can take up to an hour to run these benchmarks. The time requirement will only go up with more benchmarks.

Additional arguments:
- `--filter=benchmark_name` can be used to filter benchmarks
- `--help` will show you help about pyperf's inbuilt arguments. Refer [pyperf docs](https://pyperf.readthedocs.io/en/latest/runner.html) for more info.
- Important pyperf commands:
   - `-p5` can be used for a quick and dirty benchmark run consisting of only 5 outer runs.
   - `-o output.json` can be used to store detailed results for analysis later.
   - `pyperf compare_to` compares two results and applies statistical significance tests.
   - `pyperf timeit` is useful for measuring tiny operations like setting an attribute on an object.

#### Getting reliable results

Your local setup might not be fit for benchmarking. Follow these steps before running benchmarks:

0. Use a Linux machine. We don't run our servers on a Mac, so benchmarking on a Mac is sub-optimal.
1. Stop all unnecessary running processes. Even your browser.
2. If you're using a laptop, then plug it in. Do NOT benchmark on battery power.
3. Disable SMT (HyperThreading) - `echo "off" | sudo tee /sys/devices/system/cpu/smt/control`
4. Disable turbo boost. This is dependent on your CPU make and kernel version.
5. Use `performance` governor. - [Arch Wiki](https://wiki.archlinux.org/title/CPU_frequency_scaling)
6. Disable ASLR - `echo 0 | sudo tee /proc/sys/kernel/randomize_va_space`

This should get you roughly +/- 1% standard deviation results.

You can read this post for long-form explanations: https://ankush.dev/p/reliable-benchmarking


### Writing Microbenchmarks

1. Find appropriate `bench_{module}.py` file.
2. Add a new function with `bench_` prefix, the function body is your benchmark.
3. If you need to measure something very small (<1ms), then use `NanoBenchmark` class instead of function-based benchmarks.
4. Be very cautious about how you write a benchmark, ensure that it _actually_ measures what you want to measure. E.g. If you want to measure the performance of `frappe.get_cached_doc` when it fetches data from Redis then you need to ensure that it's not just using a locally cached document.


### E2E load testing

This repo contains a TPC-C inspired benchmark and load testing script for ERPNext.

#### Pre-requisites

- New site with ERPNext installed.
- Grafana K6 - [Installation Guide](https://grafana.com/docs/k6/latest/set-up/install-k6/)
- Basic understanding of how Frappe, ERPNext, and K6 work.

#### Usage

We use k6 to generate load. You can read their [documentation](https://grafana.com/docs/k6/latest/get-started/) to get started.

```bash
# Setup dummy master data for load testing
bench --site test_site setup-loadtest-data
# Run the load test with 100 virtual concurrent users
k6 run --vus 100 --duration 10m -e BASE_URL=http://sitename:port ./apps/caffeine/caffeine/loadtest/script.js
```

Note: fixture records have hard-coded naming to simplify writing tests without sending too many arguments. We intend to make it flexible over time if required.

#### Tweaking / Extending

If you want to write custom benchmarks, consider forking the repository or creating a new script.
The goal of this project, as of now, is to just provide the boilerplate required for writing such tests.

The following variations are worth exploring in the future:

- Realistic think times. This repo has an aggressive high-throughput API ingestion scenario. If your service will only be used by humans, then you can relax the think times.
- Read heavy workloads. This repo has a disproportionately high W:R ratio. Most sites used by end users directly will have 1:10 write-to-read ratio.
- Different modules and doctypes. Currently, we just do sales invoice -> payment -> Delivery simulation.
- Randomness / Markov modelling on top of end-user traces / complex workflows


### Contributing

At present, this repo is not accepting any external contributions.

### License

AGPL-3.0
