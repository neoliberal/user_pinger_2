# This file isn't actually run yet - it's just here to remind me to write it

except praw.exceptions.APIException as ex:
    # Check if account is deleted/suspended
    error_types = [sub_exc.error_type for sub_exc in ex.items]
    if "USER_DOESNT_EXIST" or "INVALID_USER" in error_types:
        self.logger.warning(
            "%s user %s is likely deleted/suspended",
            comment.id, 
            str(comment.author)
        )
    else:
        self.logger.error(
            "%s Unknown error pinging %s", comment.id, user
        )
