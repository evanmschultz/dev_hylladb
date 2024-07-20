Write in a way that hides internal functionality from the IDE and user, so there is a reduction in the possibility of misuse. Yet, make sure to clearly define code that is used internally, such that a user can easily track down what the code does by following the functions or classes called from the internal code in the external facing code.

Example:

```Python

import some_module as some_module

def external_face_function():
    something = some_module.some_function()
    do_something(something)
```

This ensures users can easily follow the code by holding cmd or ctrl and clicking on the function or class to see its definition and what it does.
