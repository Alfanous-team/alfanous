/* Copyright (c) 2005 Nokia Corporation
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
 */
#ifndef __SDKVERSION_H
#define __SDKVERSION_H 

#define PYS60_VERSION_MAJOR 1
#define PYS60_VERSION_MINOR 4
#define PYS60_VERSION_MICRO 5
#define PYS60_VERSION_TAG "final"
#define PYS60_VERSION_STRING "1.4.5 final"
#define PYS60_VERSION_SERIAL 0
/* For some reason the S60 SDK doesn't define any macro that contains
 * its' version, so we have to do it by ourselves. */
#define SERIES60_VERSION 30
#define S60_VERSION 30

#if 0
#define OMAP2420
#endif

#endif /* __SDKVERSION_H */
