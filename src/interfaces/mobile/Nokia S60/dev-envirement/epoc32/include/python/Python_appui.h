/*
 * ====================================================================
 *  Python_appui.h
 *  
 * Copyright (c) 2005 Nokia Corporation
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

#ifndef __PYTHON_APPUI_H
#define __PYTHON_APPUI_H

#include <coecntrl.h>
#include <eiklbo.h>
#include <aknenv.h>
#include <aknappui.h>
#include <aknapp.h>
#include "CSPyInterpreter.h"
#include <Python.rsg>
#include "symbian_python_ext_util.h"

class CAmarettoAppUi;

enum ScreenMode {
    ENormal = 0,
    ELarge,
    EFull};

class CAmarettoCallback : public CBase {
 public:
  CAmarettoCallback(CAmarettoAppUi* aAppUi):iAppUi(aAppUi) {;}
  virtual ~CAmarettoCallback() {;}
  void Call(void* aArg=NULL);

 protected:
  CAmarettoAppUi* iAppUi;

 private:
  virtual TInt CallImpl(void* aArg)=0;
};

struct SAmarettoEventInfo
{
  enum TEventType {EKey};
  TEventType iType;
  /* TCoeEvent iControlEvent; */
  TKeyEvent iKeyEvent;
  /* TEventCode iEventType; */
};

#define KMaxPythonMenuExtensions 30
#define EPythonMenuExtensionBase 0x6008

#ifndef EKA2
class CAmarettoAppUi : public CAknAppUi
#else
NONSHARABLE_CLASS(CAmarettoAppUi) : public CAknAppUi
#endif
{
 public:
  CAmarettoAppUi(TInt aExtensionMenuId): aSubPane(NULL), iExtensionMenuId(aExtensionMenuId) {;}
  void ConstructL(); 

  ~CAmarettoAppUi();

  IMPORT_C void RunScriptL(const TDesC& aFileName, const TDesC* aArg=NULL);

  TBool ProcessCommandParametersL(TApaCommand, TFileName&, const TDesC8&);
  friend TInt AsyncRunCallbackL(TAny*);
  void ReturnFromInterpreter(TInt aError);

  TInt EnableTabs(const CDesCArray* aTabTexts, CAmarettoCallback* aFunc);
  void SetActiveTab(TInt aIndex);
  TInt SetHostedControl(CCoeControl* aControl, 
                        CAmarettoCallback* aFunc=NULL);
  void RefreshHostedControl();
  void SetExitFlag() {iInterpreterExitPending = ETrue;}
  void SetMenuDynInitFunc(CAmarettoCallback* aFunc) {iMenuDynInitFunc = aFunc;}
  void SetMenuCommandFunc(CAmarettoCallback* aFunc) {iMenuCommandFunc = aFunc;}
  void SetExitFunc(CAmarettoCallback* aFunc) {iExitFunc = aFunc;}
  void SetFocusFunc(CAmarettoCallback* aFunc) {iFocusFunc = aFunc;}

  struct TAmarettoMenuDynInitParams {
    TInt iMenuId;
    CEikMenuPane *iMenuPane;
  };

  TInt subMenuIndex[KMaxPythonMenuExtensions];
  void CleanSubMenuArray(); 
  void SetScreenmode(TInt aMode);

  CCoeControl* iContainer;
  CEikMenuPane* aSubPane;

 private:
  void HandleCommandL(TInt aCommand);
  void HandleForegroundEventL(TBool aForeground);
  void HandleResourceChangeL( TInt aType);

  void DynInitMenuPaneL(TInt aMenuId, CEikMenuPane* aMenuPane);

  void DoRunScriptL();
  void DoExit();

  CSPyInterpreter* iInterpreter;
  CAmarettoCallback* iMenuDynInitFunc;
  CAmarettoCallback* iMenuCommandFunc;
  CAmarettoCallback* iExitFunc;
  CAmarettoCallback* iFocusFunc;
  TBool iInterpreterExitPending;
  TInt iExtensionMenuId;
  CAsyncCallBack* iAsyncCallback;
  TBuf<KMaxFileName> iScriptName;
  TBuf8<KMaxFileName> iEmbFileName;
  TInt iScreenMode;
};

IMPORT_C CEikAppUi* CreateAmarettoAppUi(TInt);

#endif /* __PYTHON_APPUI_H */
