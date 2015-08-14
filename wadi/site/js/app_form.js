// Generated by CoffeeScript 1.9.3
(function() {
  angular.module('Wadi.form', []).controller('FormCtrl', function($scope, $state, $log, $http) {
    var configureForm;
    $scope.checkLogin = function() {
      $log.info("Checking login status at FormCtrl");
      if (!$scope.$parent.checkLogin()) {
        return $state.go('login');
      }
    };
    $http.get('http://45.55.72.208/wadi/interface/form').success(function(data) {
      return configureForm(data);
    });
    $scope.multi = {};
    $scope.single = {};
    $scope.selectedMulti = {};
    $scope.selectedSingle = {};
    return configureForm = function(mainData) {
      var data, i, len;
      for (i = 0, len = mainData.length; i < len; i++) {
        data = mainData[i];
        if (data.type === 'single') {
          $scope.single[data.operation] = {
            name: data.pretty,
            values: data.values
          };
          $scope.selectedSingle[data.operation] = [];
        } else {
          $scope.multi[data.operation] = {
            name: data.pretty,
            values: data.values
          };
          $scope.selectedMulti[data.operation] = [];
        }
      }
      $log.info("Singles: " + JSON.stringify($scope.single));
      return $log.info("Multi: " + JSON.stringify($scope.multi));

      /*
        $scope.submit = () ->
      result = {}
      result['target_config'] = formPartial()
      result['campaign'] = $scope.campaign
      $log.info "Posting: "+JSON.stringify(result)
      
      $http.post('http://45.55.72.208/wadi/interface/post', result)
      .success (res) ->
        $log.info "Got result: "+JSON.stringify(res)
       */
    };
  });

}).call(this);

//# sourceMappingURL=app_form.js.map
