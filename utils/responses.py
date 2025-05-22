from sqlite.schemas import CommonResponseClass


def common_responses():
    return {
        400: {"model": CommonResponseClass},
        401: {"model": CommonResponseClass},
        404: {"model": CommonResponseClass},
        403: {"model": CommonResponseClass},
    }
