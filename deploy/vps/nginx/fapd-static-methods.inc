# A static path answers GET and HEAD and nothing else. `if … return` in
# a location is one of the two documented safe uses of `if`. Rewrite-
# module directives are not inherited by nested locations, so every
# location includes this itself.
if ($request_method !~ ^(GET|HEAD)$) { return 405; }
