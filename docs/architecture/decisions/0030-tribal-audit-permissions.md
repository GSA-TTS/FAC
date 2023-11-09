# 30. Introduce user permissions for tribal audit access

Date: 2023-11-08

## Status

Accepted

## Areas of impact

*   Engineering

## Context
We need a mechanism for allowing federal users to access tribal audit data through web search.

Currently, the search feature does not require users to be authenticated, and therefore we do not perform any authorization checks on the backend. As a consequence, all tribal audit data is being omitted from the search results.

## Decision
We will create a new `Permission` model in the `users` app:

```python
class Permission(models.Model):
    slug = models.CharField(max_length=255)  # e.g. "read-tribal"
    description = models.TextField()  # e.g. "Can read tribal audit data"
```

This table will hold the canonical set of permissions that can be granted to a user. Initially, there will only be one: the ability to read tribal audit data.

We will create a new `UserPermission` model in the `users` app that associates a `User` (or an `email` in the case where no `User` with the provided email yet exists in the FAC system) with a `Permission`:

```python
class UserPermission(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, null=True)
    permission = models.ForeignKey(Permission)
```

`UserPermissions` can be created given only an email address. The next time the user with that email address logs into the FAC, any as-yet unclaimed `UserPermission` objects in the database will be claimed and the foreign key relationship to the actual `User` object will be established (this is similar to how we currently manage `Access` objects on the intake side).

Permission checks should be performed through centrally located convenience functions to minimize references to permission slugs being spread out over the code base, such as:

```python
def can_read_tribal(user):
    user_permissions = UserPermission.objects.filter(user=user, permission__slug="read-tribal")
    return len(user_permissions) > 0
```

The `Search` view will be updated such that the search behavior for unauthenticated users remains unchanged. If, however, an authenticated user executes a search, we will check to see if the user holds the `read-tribal` permission. If they do, non-public submission data will be included in the search results.

The [search function](https://github.com/GSA-TTS/FAC/blob/2e56df478dda9f1b5d2e4971fda64d6fdd49cbd5/backend/dissemination/search.py#L6) is currently hard-coded to omit non-public results. We will update this function to accept an `include_non_public` argument, which defaults to False. It will the responsibility of the [search view](https://github.com/GSA-TTS/FAC/blob/2e56df478dda9f1b5d2e4971fda64d6fdd49cbd5/backend/dissemination/views.py#L27) to determine whether or not non-public results should be included before calling `search_general`. This way, `search_general` could, in theory, be reused for API-based search in the future, where the specific authorization mechanism will likely be different.

## Consequences
- `UserPermissions` can be managed through Django admin
- The initial set of permission types and any new permission types created in the future should be added using a [data migration](https://docs.djangoproject.com/en/4.2/topics/migrations/#data-migrations) to keep things consistent across environments and and visible in source control.