import math


def relative_size_change(current, previous):
    return int(abs(((current - previous) / previous) * 100))


def allowed_size_change(bytesize):
    '''Calculate the maximum allowed change percentage.

    bytesize should be the initial size of the file in bytes. We then use a
    function that calculates the maximum allowed percentage the file can grow.

    The logic behind this is that really small files should be allowed to grow
    by a larger percentage than large files:

    When a 200kB file grows by 200% to 600kB, it's not a big deal; When a 2GB
    file grows to 6GB, it is.

    This function is based on the calculations in docs/backup_check.numbers

    The curve can be influenced by changing the variables below, you can try
    different combinations in the Numbers spreadsheet.
    '''

    n = 4000
    a = 4
    div = 2
    inc = 2.5
    dec = 2

    # The minimum percentage to allow
    minimum_percentage = 2

    order_of_magnitude = math.log10(bytesize)

    allowed_percentage = (
        math.exp(
            dec - math.sqrt(a * math.pow(order_of_magnitude, 2) + inc) / div
        ) * n
    )

    # Return the largest of the 2 percentages. This makes sure that when
    # allowed_percentages goes below minimum_percentage, minimum is returned
    return int(max(minimum_percentage, allowed_percentage))
