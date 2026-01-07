---
created: 2025-07-19T15:35:24 (UTC -04:00)
tags:
  - widows
  - software
source: https://kb.uwec.edu/articles/drives-establishing-windows-file-and-folder-level-permissions
author:
---

# Network: Establishing Windows File and Folder Level Permissions

> ## Excerpt
> In many cases, you will need to change the permissions that a certain group or individual user has to a file or folder. For example, you can designate a ...

---
In many cases, you will need to change the permissions that a certain group or individual user has to a file or folder. For example, you can designate a special folder on the W**:** drive within your department's area called "Incoming" as a place where students can turn in their work. To do this, you would first need to create a new folder on the W: drive. By default, the new folder will have the same permissions as the parent folder, which would not allow students to submit their work, and may not allow students to even access the folder. You would then need to allow students access to the new folder, and set permissions for the folder. When you set permissions, you are specifying what level of access students have to the folder and its files and what students can do within that folder such as save, delete, or read files.

_NOTE: The majority of these instructions refer to Computer in the Start Menu._

## [Standard Permission Types](https://kb.uwec.edu/articles/drives-establishing-windows-file-and-folder-level-permissions#standard-permission-types)
-------------------------------------------------------------------------------------------------------------------------------------------------

There are six standard permission types which apply to files and folders in Windows:

-   Full Control
-   Modify
-   Read & Execute
-   List Folder Contents
-   Read
-   Write

Each level represents a different set of actions users can perform. See the table below for more information.

For folders you can also set your own unique permissions or create a variation on any of the standard permission levels. Within each of the permission levels are many possible variations. For information on some of these advanced options, refer to _Advanced Folder Level Permissions_ below.

The following table represents the available standard permission types. 

Full ControlPermits the user(s) to:

-   view file name and subfolders.
-   navigate to subfolders.
-   view data in the folder's files.
-   add files and subfolders to the folder.
-   change the folder's files.
-   delete the folder and its files.
-   change permissions.
-   take ownership of the folder and its files.

ModifyPermits the user(s) to:

-   view the file names and subfolders.
-   navigate to subfolders.
-   view data in the folder's files.
-   add files and subfolders to the folder.
-   change the folder's files.
-   delete the folder and its files.
-   open and change files.

Read & ExecutePermits the user(s) to:

-   view file names and subfolder names.
-   navigate to subfolders.
-   view data in the folder's files.
-   run applications.

List Folder ContentsPermits the user(s) to:

-   view the file names and subfolder names.
-   navigate to subfolders.
-   view folders.
-   does not permit access to the folder's files.

ReadPermits the user(s) to:

-   view the file names and subfolder names.
-   navigate to subfolders.
-   open files.
-   copy and view data in the folder's files.

WriteThe Read permissions, plus permits the user(s) to:

-   create folders.
-   add new files.
-   delete files.

## [ Create a New Folder ](https://kb.uwec.edu/articles/drives-establishing-windows-file-and-folder-level-permissions#create-a-new-folder)
-----------------------------------------------------------------------------------------------------------------------------------------

In many cases you will need to create a new folder. If you are using an existing folder and do not wish to create a new folder, continue with _Accessing the Properties Dialog Box_.

1.  Click on the **Start** menu**.  
    **  
    
2.  Click **Computer.  
    **  
    
3.  From the _Computer_ window, select the shared drive for your area or department (_S Drive_ or _W Drive_).
4.  Navigate to the location you want the new folder to appear (e.g., within one of your existing folders).
5.  On the menu bar, select **_New Folder._**  
    OR  
    Right click » select **_New_** » select **_Folder._**  
    A new folder is created which inherits the security permissions of its "parent."  
     
6.  In the newly created folder, type the desired folder name.
7.  Press \[Enter\] or click off of the folder.

## [ Accessing the Properties Dialog Box ](https://kb.uwec.edu/articles/drives-establishing-windows-file-and-folder-level-permissions#accessing-the-properties-dialog-box)
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

When working with permissions in Windows 7, you are required to work from the _Properties_ dialog box. This dialog box for the file or folder you are working with can be accessed in a few steps.

1.  Click on the **Start** menu**.  
    **  
    
2.  Click **Computer.  
    **  
    
3.  Select the folder or file you wish to adjust/view permissions for.
4.  Right-click the folder or file.
5.  Select **_Properties_**.  
    The _Properties_ dialog box appears.

## [ Granting Access to a File or Folder ](https://kb.uwec.edu/articles/drives-establishing-windows-file-and-folder-level-permissions#granting-access-to-a-file-or-folder)
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

After creating a new folder, or even if you will use an existing folder, you will need to determine who will have access to it. Also, keep in mind that by default the same persons who have access to the "parent" (original) folder also have access to the new folder, and vice versa. This may not be ideal. It is a simple process to grant access to specific users for any folder you have created.

1.  Access the _Properties_ dialog box.
2.  Select the **_Security_** tab.
    
    ![](https://uwecwebdev.blob.core.windows.net/knowledgebase/wve279hegtl3iiklilcn7i67gg5n)
    
3.  Click **Edit**.  
    The _security_ tab opens in a new window.  
4.  Click **Add**...  
    The _Select Users, Computers_, _or_ _Groups_ dialog box appears.
    
    ![](https://uwecwebdev.blob.core.windows.net/knowledgebase/zf7z6d0ox77fwvpnk2nxj110yeqx)
    
5.  In the _Enter the object names to select_ text box, type the name of the user or group that will have access to the folder (e.g., 2125.engl.498.001 or username@uwec.edu).
    
    _HINT: You may type the beginning of the name and then click_ **_Check Names_**_. The name will either be resolved or a list of users beginning with those characters will display for you to select from._
    
6.  Click **OK**.  
    The _Properties_ dialog box reappears.  
     
7.  Click **OK** on the _Security_ window.
8.  Continue with _Setting Permissions_ below.

## [ Setting Permissions ](https://kb.uwec.edu/articles/drives-establishing-windows-file-and-folder-level-permissions#setting-permissions)
-----------------------------------------------------------------------------------------------------------------------------------------

Once you have granted a group or individual user access to a folder, you will need to set permissions for the new user(s). When you set permissions, you are specifying what level of access a user(s) has to the folder and the files within it. Be careful about checking _Deny_ for any permissions, as the _Deny_ permission overrides any other related to _Allow_ permissions.

Folder permissions can be changed only by the owner of the folder (i.e., the creator) or by someone who has been granted permission by the owner. If you are not the owner of the folder or have not been granted permission by the owner, all checkboxes will be gray. Therefore, you will not be able to make any changes until the owner grants you permission.

1.  Access the _Properties_ dialog box.
2.  Select the **_Security_** tab.  
    The top portion of the dialog box lists the users and/or groups that have access to the file or folder.  
3.  Click **Edit**
    
    ![](https://uwecwebdev.blob.core.windows.net/knowledgebase/opnwvtxt7el2311nc8rkly1rdxcj)
    
4.  In the _Group or user name_ section, select the user(s) you wish to set permissions for
5.  In the _Permissions_ section, use the checkboxes to select the appropriate permission level
6.  Click **Apply  
    **  
7.  Click **Okay**  
    The new permissions are added to the file or folder.

## [ Advanced Folder Level Permissions ](https://kb.uwec.edu/articles/drives-establishing-windows-file-and-folder-level-permissions#advanced-folder-level-permissions)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------

When you set permissions, you specify what users are allowed to do within that folder, such as save and delete files or create a new folder. You are not limited to choosing one of the standard permissions settings (_Full Control, Modify, Read & Execute, List Folder Contents, Read_, or _Write_). Instead of choosing one of these settings, you may set your own unique permissions based on what you would like users to be able to do. For an understanding of how options can be combined, refer to Permission Types: An Overview.

Remember, folder permissions can only be changed by the owner of the folder (i.e., the creator) or by someone who has been granted permission by the owner. If you are not the owner of the folder or have not been granted permission by the owner, the checkboxes will be grayed out. Therefore, you will not be able to make any changes until the owner grants you permission.

1.  Access the _Properties_ dialog box
2.  Select the **_Security_** tab
3.  Near the bottom right of the _Properties_ dialog box, click **Advanced**  
    The _Advanced Security Settings_ dialog box appears.
    
    ![](https://uwecwebdev.blob.core.windows.net/knowledgebase/rwv0cphnc2vzotf465ftzufjdoka)
    
      
     
4.  (Optional) If you do not want the new folder to have the same permissions as the "parent" (original) folder and wish to set unique permissions for the new folder, click the **Change Permission** button near the bottom. This will bring up a similar window.
    1.  Uncheck the **_Include inheritable permissions from this object's parent_** checkbox  
        A _Windows Security_ warning dialog box will appear.  
        
        ![](https://uwecwebdev.blob.core.windows.net/knowledgebase/ka520iibpo56jmy48gle2uka39s2)
        
          
         
    2.  Click **Remove** if you want someone removed from permission all together  
        _NOTE: Read the instructions carefully and choose the action you wish to have taken for permissions._  
         
5.  Click the **Change Permissions** button
6.  Select the appropriate user  
    OR  
    Click **Add** and enter the name of the user or group that will have access to the folder.  
     
7.  Click **Edit**...  
    The _Permissions Entry_ dialog box appears.
    
    ![](https://uwecwebdev.blob.core.windows.net/knowledgebase/6v8ut147jv487khfrqppng3d9y89)
    
      
     
8.  In the _Permissions_ section, use the checkboxes to set the appropriate permissions
    
    _NOTE: If you are not the owner of the folder or have not been granted permission by the owner, all checkboxes will be gray. Therefore you will not be able to make any changes until the owner grants you permission to do so._
    
9.  From the _Apply to:_ pull-down list, select what level you wish to apply these permissions to
10.  Click **OK  
    **  
11.  In the _Advanced Security Setting_ dialog box, click **OK  
    **  
12.  Click **OK** from the duplicate _Advanced Security Settings  
13.  In the _Properties_ dialog box, click **OK**  
    The new folder permissions are added for your specified user(s).