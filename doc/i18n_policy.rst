Internationalization policy
===========================

ReVot is internationalized following the guidelines below:

1. User interface uses the language and datetime provided by the web
   client used during navigation. Language is obtained by negotiation
   with the web client and datetime localization is assumed by the
   javascript library `momentjs`.

2. A voting has a language associated. The end user chooses this
   language when setting up a voting.  Votation descriptions, question
   and options are assumed to be written in this single language.

3. Ballot mails are allways sent in the voting language and datetime
   is localitzed using the Barcelona time zone. There are no other
   chance because there is no automatic way to know the mail receiver
   preferences.
