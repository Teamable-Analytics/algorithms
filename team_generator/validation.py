def validate_unique_fields(items, exception_cls, field, set_name):
    id_set = []
    for d in items:
        if d[field] in id_set:
            raise exception_cls(
                f'The field "{field}" must be unique for each element of the set of "{set_name}"\n'
                f'Cannot add the duplicate {d[field]} to {id_set}'
            )
        id_set.append(d[field])
