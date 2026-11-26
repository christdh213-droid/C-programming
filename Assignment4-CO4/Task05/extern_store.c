int shared_token=1000;
int external_next(void) { return ++shared_token; }
int shared_two_tokens[2]={1000,1000};
int external_two_next(int which) { return ++shared_two_tokens[which]; }
