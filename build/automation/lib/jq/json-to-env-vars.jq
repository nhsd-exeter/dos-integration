to_entries|map("\(.key)=\(.value|tostring)")|.[]
