def are_object_to_edit_and_other_object_same(
    obj_to_edit, other_object_with_same_unique_field
) -> bool:
    """Check if the object you are editing is the same as the second object, or it violates a unique constraint"""
    return True if obj_to_edit.id == other_object_with_same_unique_field.id else False
