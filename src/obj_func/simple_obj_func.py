# a simple object function
# accept when performance > 10% and max_drawdown < 10%


def accept(results):
    cur_results, perf_stats = results

    return perf_stats['Annual return'] > 0


def better_results(cur_results, prev_results):
    if prev_results is None:
        return True

    results, perf_stats = cur_results
    prev_results, prev_perf_stats = prev_results

    delta = perf_stats['Annual return'] - prev_perf_stats['Annual return']

    if delta > 0.01:
        return True

    if delta >= -0.01:
        return abs(perf_stats['Max drawdown']) < abs(prev_perf_stats['Max drawdown'])

    return False
