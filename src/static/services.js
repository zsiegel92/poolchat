'use strict'

angular.module('myApp').factory('AuthService',
  ['$q', '$timeout', '$http','$log',
  function ($q, $timeout, $http, $log) {

    // create user variable
    var user = null;

    // return available functions for use in controllers
    return ({
      isLoggedIn: isLoggedIn,
      login: login,
      logout: logout,
      register: register,
      getUserStatus: getUserStatus
    });

    function isLoggedIn() {
      if(user) {
        return true;
      } else {
        return false;
      }
    }

    function login(email, password,remember_me) {

      $log.log("Trying to log in with email " + email + " and p-word xxxx");
      var resp= $http.post('/api/login',
                $.param({email: email, password: password,remember_me: remember_me}),
                {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
      // send a post request to the server
        // handle success
        .then(function (response) {
          if(response.status === 200){
            $log.log("logged in")
            user = true;
            return response;
          } else {
            $log.log("Error in services.Authservice.login");
            user = false;
            return response;
          }
        })
        // handle error
        .catch(function (response) {
          $log.log("Error in services.Authservice.login");
          user = false;
          return response;
        });

      // return promise object
      return resp;

    }


    function frontend_logout(){
      user=false;
    }

    function logout() {

      // create a new instance of deferred
      var deferred = $q.defer();

      // send a get request to the server
      $http.get('/api/logout')
        // handle success
        .then(function (response) {
          user = false;
          deferred.resolve();
        })
        // handle error
        .catch(function (response) {
          user = false;
          deferred.reject();
        });

      // return promise object
      return deferred.promise;

    }

    function register(first,last,email, password,confirm,accept_tos) {

// ,firstname,lastname,accept_tos
      // create a new instance of deferred
      // var deferred = $q.defer();
      // send a post request to the server
      var resp= $http.post('/api/register', $.param({firstName: first, lastName: last, email: email, password: password,confirm: confirm, accept_tos: accept_tos}),{headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        // handle success
        .then(function (response) {
          if(response.status === 200){
            // deferred.resolve();
            $log.log("Registered");
            return response;
          } else {
            // deferred.reject();
            $log.log("error");
            return response;
          }
        })
        // handle error
        .catch(function (response) {
          // $log.log(response.data);
          // deferred.reject();
          return response;
        });
        return resp;
      // // return promise object
      // return deferred.promise;
    }

    function getUserStatus() {
      return $http.get('/api/status')
      // handle success
      .then(function (response) {
        if(response.data.status){
          user = true;
        } else {
          user = false;
        }
      })
      // handle error
      .catch(function (response) {
        user = false;
      });
    }

}]);
