
function sort_unique(arr) {
    arr = arr.sort(function (a, b) { return a*1 - b*1; });
    var ret = [arr[0]];
    for (var i = 1; i < arr.length; i++) { // start loop at 1 as element 0 can never be a duplicate
        if (arr[i-1] !== arr[i]) {
            ret.push(arr[i]);
        }
    }
    return ret;
}

var app = angular.module('HealthApp', ['ngAnimate', 'ngResource', 'google-maps']);

app.factory('Geocoder', function() {
  return new google.maps.Geocoder();
});

app.factory('Results', function($resource) {
  return $resource('results.json', {  });
});

app.controller('DataCtrl', ['$scope', '$filter', '$timeout', 'Results', 'Geocoder', function($scope, $filter, $timeout, Results, Geocoder) {

    $scope.cat_lvl_1 = [];
    $scope.cat_lvl_2 = [];
    $scope.cat_lvl_3 = [];

    $scope.cities = [];
    $scope.markers = [];
    $scope.search = {city: ""};
    $scope.highlighted = [];

    $scope.items = Results.query(function() {

        $scope.cat_lvl_1 = $scope.items[0];
        $scope.cat_lvl_2 = $scope.cat_lvl_1.ch[12];

        console.log("Finished Loading");
    });

    $scope.map = {
        refresh: false,
        center: {
            latitude: 46.567488,
            longitude: 6.68096420
        },
        zoom: 11
    };

    window.map = $scope.map;

    $scope.$watch("search.city", function(newValue, oldValue) {

        $scope.centerMap();
        $scope.drawMarkers();
    });

    $scope.centerMap = function() {

        Geocoder.geocode({ 'address': $scope.search.city}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                var pos = results[0].geometry.location;
                $scope.map.center = {
                    latitude: pos.k,
                    longitude: pos.B
                };
            }
        });
    };

    $scope.drawMarkers = function() {

        $scope.markers = [];
        var items = $filter('filter')($scope.cat_lvl_2.ch, $scope.search);

        angular.forEach(items, function(item, key) {
            $timeout(function () {
                Geocoder.geocode( { 'address': item.city + ", " + item.address}, function(results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {
                        var pos = results[0].geometry.location;
                        $scope.markers.push(
                            {pos: {latitude: pos.k, longitude: pos.B}, name: item.name, id: item.id,
                             onClick: function() {
                                 item.highlighted = true;
                             }}
                        );
                        $scope.map.refresh = true;
                    }
                    else {
                        console.error(status);
                    }
                });
            }, (key + 1) * 650);
        });
    };

    $scope.$watch("cat_lvl_2", function(newValue, oldValue) {

        var cities = [];

        angular.forEach($scope.cat_lvl_2.ch, function(item) {

            cities.push(item.city);
        });

        $scope.cities = cities.sort().filter(function(el,i,a){return i==a.indexOf(el);});
        $scope.search.city = $scope.cities[0];
    });

}]);