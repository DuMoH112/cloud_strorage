
# Bars Group

Реализация задачи для хакатона Bars Group "Битва стеков": “Разработать типовой функционал информационной системы для хранения и доступа к этим файлам (своеобразное облачное хранилище)”

## Start project
Проект разворачивается при помощи docker-compose

## Indices

* [Drive](#drive)

  * [Create directory Copy](#1-create-directory-copy)
  * [Del object](#2-del-object)
  * [Get file](#3-get-file)
  * [Get files in directory](#4-get-files-in-directory)
  * [Get share](#5-get-share)
  * [Share object](#6-share-object)
  * [Upload file](#7-upload-file)

* [Personal area](#personal-area)

  * [Auth](#1-auth)
  * [Get users list](#2-get-users-list)
  * [Register](#3-register)


--------


## Drive



### 1. Create directory Copy



***Endpoint:***

```bash
Method: POST
Type: RAW
URL: {{url}}/create_folder
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Body:***

```js        
{
    "file_path": "/Folder/Photo"
}
```



### 2. Del object



***Endpoint:***

```bash
Method: DELETE
Type: RAW
URL: {{url}}/del_object
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Body:***

```js        
{
    "file_path": "/Intermediate_Python_M_Khalid.pdf.zip"
}
```



### 3. Get file



***Endpoint:***

```bash
Method: POST
Type: RAW
URL: {{url}}/get_file
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Body:***

```js        
{
    "file_path": "/Intermediate_Python_M_Khalid.pdf.zip"
}
```



### 4. Get files in directory



***Endpoint:***

```bash
Method: POST
Type: RAW
URL: {{url}}/get_files_in_directory
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Body:***

```js        
{
    "file_path": "/"
}
```



### 5. Get share



***Endpoint:***

```bash
Method: GET
Type: 
URL: http://rdbkzn.ru:5555/share
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Query params:***

| Key | Value | Description |
| --- | ------|-------------|
| route | %2FAdmin%2FIntermediate_Python_M_Khalid.pdf.zip |  |
| type | file |  |



### 6. Share object



***Endpoint:***

```bash
Method: POST
Type: RAW
URL: {{url}}/share
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Body:***

```js        
{
    "file_path": "/Intermediate_Python_M_Khalid.pdf.zip"
}
```



### 7. Upload file



***Endpoint:***

```bash
Method: POST
Type: FORMDATA
URL: {{url}}/upload_file
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Body:***

| Key | Value | Description |
| --- | ------|-------------|
| file |  |  |
| file_path | / |  |



## Personal area



### 1. Auth



***Endpoint:***

```bash
Method: 
Type: 
URL: 
```



### 2. Get users list



***Endpoint:***

```bash
Method: GET
Type: 
URL: {{url}}/back/users_list
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



### 3. Register



***Endpoint:***

```bash
Method: POST
Type: RAW
URL: {{url}}/back/registration
```


***Headers:***

| Key | Value | Description |
| --- | ------|-------------|
| Token | {{Token}} |  |
| UserToken | {{UserToken}} |  |



***Body:***

```js        
{
    "username": "Client1",
    "password": "Q1wfsdfuihqq",
    "confirm_password": "Q1wfsdfuihqq",
    "size_space_kbyte": 102400
}
```



---
[Back to top](#bars-group)
> Made with &#9829; by [thedevsaddam](https://github.com/thedevsaddam) | Generated at: 2021-04-11 14:11:36 by [docgen](https://github.com/thedevsaddam/docgen)
