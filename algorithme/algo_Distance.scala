import org.apache.spark.sql.hive.HiveContext
import org.apache.spark.sql.functions

case class Location(lat: Double, lon: Double)

def calculDistance(locationA: Location, locationB: Location): Double = {
    val latDistance = Math.toRadians(locationA.lat - locationB.lat)
    val lngDistance = Math.toRadians(locationA.lon - locationB.lon)
    val sinLat = Math.sin(latDistance / 2)
    val sinLng = Math.sin(lngDistance / 2)
    val a = sinLat * sinLat +
    (Math.cos(Math.toRadians(locationA.lat))
    * Math.cos(Math.toRadians(locationB.lat))
    * sinLng * sinLng)
    val c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    val AVERAGE_RADIUS_OF_EARTH_KM = 6371
    AVERAGE_RADIUS_OF_EARTH_KM * c
    }
	val a = new Location(14.696537, -17.448955)
	val b = new Location(14.705296, -17.456594)
	
	// Site to check http://boulter.com/gps/distance/
	
	// P1 = 14.696537, -17.448955
	// 14.705296, -17.456594

