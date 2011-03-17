/*
* ====================================================================
*  CSPyInterpreter.h
*  
*  An interface for creating/deleting a Python interpreter instance
*  and some convenience functions for simple interaction with it.     
*
* Copyright (c) 2005-2008 Nokia Corporation
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
* ====================================================================
*/

#ifndef __CSPYINTERPRETER_H
#define __CSPYINTERPRETER_H

#include <e32std.h>
#include <e32base.h>
#include <stdio.h>
#include <errno.h>

#ifndef EKA2
class CSPyInterpreter : public CBase {
#else
NONSHARABLE_CLASS(CSPyInterpreter) : public CBase {
#endif  
 public:
  IMPORT_C static CSPyInterpreter*
    NewInterpreterL(TBool aCloseStdlib = ETrue,
                    void(*aStdioInitFunc)(void*) = NULL,
                    void* aStdioInitCookie = NULL);

  CSPyInterpreter(TBool aCloseStdlib):
    iInterruptOccurred(0), iCloseStdlib(aCloseStdlib) {;}

  IMPORT_C virtual ~CSPyInterpreter();

  IMPORT_C TInt RunScript(int, char**);
  IMPORT_C void PrintError();

  int read(char *buf, int n) {
    return (iStdI ? iStdI(buf, n) : -EINVAL);
  }
  int write(const char *buf, int n) {
    return (iStdO ? iStdO(buf, n) : n);
  }

  IMPORT_C void InitializeForeignThread();
  IMPORT_C void FinalizeForeignThread();

  TInt iInterruptOccurred;
  RHeap* iPyheap;
  void (*iStdioInitFunc)(void*);
  void* iStdioInitCookie;
  int (*iStdI)(char *buf, int n);
  int (*iStdO)(const char *buf, int n);

 private:
  void ConstructL();
  TBool iCloseStdlib;
  void *iPrivate;
};

#endif /* __CSPYINTERPRETER_H */
