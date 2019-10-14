def hl_cross_n_days(v1, v2, n):
    for i in range(n - 1):
        v = (
            True
            and all([v1[x] <= v1[i] for x in range(i + 1, n)])
            and all([v1[x] <= v2[x] for x in range(i, n)])
        )

        if v:
            return True

    return False


if __name__ == '__main__':
    print(hl_cross_n_days([74.724123
                           , 75.235747
                           , 65.824630
                           , 60.509786
                           , 56.007323],
                          [64.535724
                           , 68.102398
                           , 67.343142
                           , 65.065357
                           ,  62.046012],
                          5))
