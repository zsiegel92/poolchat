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

      // create a new instance of deferred
      var deferred = $q.defer();
      $log.log("Trying to log in with email " + email + " and p-word " + password);
      $http.post('/api/login',
                $.param({email: email, password: password,remember_me: remember_me}),
                {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
      // send a post request to the server
        // handle success
        .then(function (response) {
          if(response.status === 200 && response.data.result){
            $log.log("logged in")
            user = true;
            deferred.resolve();
          } else {
            user = false;
            deferred.reject();
          }
        })
        // handle error
        .catch(function (response) {
          user = false;
          deferred.reject();
        });

      // return promise object
      return deferred.promise;

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

    function register(email, password) {

      // create a new instance of deferred
      var deferred = $q.defer();

      // send a post request to the server
      $http.post('/api/register', {email: email, password: password})
        // handle success
        .then(function (response) {
          if(response.status === 200 && response.data.result){
            deferred.resolve();
          } else {
            deferred.reject();
          }
        })
        // handle error
        .catch(function (response) {
          deferred.reject();
        });

      // return promise object
      return deferred.promise;

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
