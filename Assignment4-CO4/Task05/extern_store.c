int shared_token=1000;
int external_next(void) { return ++shared_token; }
