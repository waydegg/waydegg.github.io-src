Title: FRC Robotics Work
Date: 2018-07-05 1:48
Modified: 2018-05-09 1:49
Tags: personal projects, robotics
Slug: frc-robotics-cad
Authors: Wayde Gilliam
Summary: My work in FRC robotics (Only Showing 2017-2018!)


Throughout high school, I spent just about all of my free time during the school year and Summer working on something related with my FRC robotics team, Team Paradox 2102. I wanted to showcase/share all of my prominent robot CAD, Tableau visualizations, and Scouting Application work in one place. If you haven't heard of [FRC robotics](https://www.youtube.com/watch?v=KlyCbntMBqU), it's essentially a world wide robotics competition amongst high schoolers where we have 6 weeks to build a robot then compete with the 1000's of teams that make up the program. It's pretty cool.


# CAD

I was the Engineering President for my team my junior and senior years, and filled into the position mid sophomore year to help with all work on the robot. A large part of my job was to lead the design of the robot, using SolidWorks as our primary CAD software when creating these machines. Below are brief summaries and descriptions of how the several robots I helped design, manufacture, and compete with all came together.

## 2017-2018 Season
### The Robot - "Lambda"

![Rendered Lambda](images/frc_cad/robot.JPG)

The Competition for this year, "Power Up", mainly consisted of placing yellow cubes on platforms low to the ground and high up in the air. The platforms tilt a certain direction depending on which team has more cubes on their assigned side, so the better you are at placing these cubes, the more points you'll get. Because of this, I and my engineering team made the main goal for our robot to be great at placing these cubes all while keeping our design and strategy at the level of experience of the students making this machine. This robot has been the team's most successful by far. We were finalists at the San Diego Regional (6 of 66 teams) & appointed the Excellence in Engineering award (1 of 66 teams), quarter finalists at the Idaho Regional (24 of 39 teams), ranked 4th and quarter finalists at the Houston World Championships in our division (32 of 67 teams), and ranked in the top 48 teams in the entire world (48 of 7,331 teams).

#### The Chassis

![Rendered Chassis](images/frc_cad/chassis.JPG)

For the past 2 years we've been perfecting our chassis design, as it's really what needs to be the strongest and most reliable part of a FRC robot, so when this year's competition came around we were very prepared. The frame of the drivetrain mainly consists of aluminum 2"x1" extrusion with 1/8" aluminum sheet metal gussets being held together by aluminum rivets. At our highschool we have several manual mills, a Tormach PCNC 1100, and a plasma cutter, so making all of our parts in-house is very doable. The end result is a simple and lightweight chassis that's easy to customize and alter for future competitions.

##### The Gearboxes

![Gearbox](images/frc_cad/gearbox1.JPG) 
![Gearbox](images/frc_cad/gearbox2.JPG)

The gearboxes this season have been one of the more ambitious things we've designed. Using 2 CIM motors each, the transmission for the robot shifts into a high ~17 ft/sec for quickly traversing the field, and a low ~2.5 ft/sec for playing defense and getting into pushing matches with opposing robots. We have a second shifter on the gearboxes that act as a PTO ("Powered Take Off") to lift ourselves and two other 120lb robots for this year's "endgame challenge". We have a theoretical lift capacity of ~500lbs with these gearboxes combined.

##### The Drivetrain

![Drivetrain](images/frc_cad/drivetrain.png)

The style of drivetrain pictured above is a "Westcoast" drivetrain (the name coming from numerous west coast teams that adopted this style a few years ago). Typically appearing in 6 and 8 wheel configurations, the center wheels are dropped 1/16" - 1/8" from the centerline of the aluminum side bars to make turning easier. We been using chain to drive everything because it last's a lot longer than belt drives, and tensioning everything is very easy as we use VEX bearing blocks, cams, and a hex head allen key to lock everything in.

#### The Elevator

![Elevator](images/frc_cad/elevator.JPG)

This mechanism is one of the more critical ones of the robot as it determines how fast we'll be able to move and place "power cubes" around the game field elements for scoring points. Our elevator has 2-stages nested inside of it, keeping the retracted height within our legal starting volume, though able to extend close to twice our starting height during our matches. We use a "Cascading" cable setup for lifting the elevator, with the intention of having a 2:1 speed ratio when powering the lifting/retracting. There are 2 lengths of steel cable (later switched out for nylon rope) attached to the middle-stage and "carriage" (inner-stage) that link everything together. With the use of pneumatics and a bike disc brake, we're able to hold the position of everything to make placing cubes much easier.

![Elevator](images/frc_cad/elevator_raised.jpg)

This is a pretty common style of elevators in FRC, though what makes ours unique is how compact & light weight it is. This was one of our goals as we set out designing this mechanism, though after finishing our first regional competition, we realized that we made everything too light, and had to go through a redesign that was finished by the FRC World Championship a few weeks later. A complete overhaul on the gusset, limit switch setup, and bearing placement to align the multiple stages literally made this mechanism indestructible throughout the remainder of our season.

#### The Intake

![Intake](images/frc_cad/intake.JPG)
![Intake](images/frc_cad/intake2.jpg)

This is another mechanism that was an integral part of our success for the season. The intake is the mechanism that acquires, secures, and places cubes for scoring, so it needed to always work if we wanted to have any ability to do well in our competitions. Our intake starts folded up vertically to fit into our starting volume, and when the match starts it drops down and a servo moves a hard-stop in place to give us an additional position to actuate to. Several powerful pneumatic pistons lift the intake and actuate it's fingers to hold onto powercubes. A series of belts and pulleys powered by dual 775 motors give the intake the necessary force to quire and launch powercubes for scoring. After many iterations, by the World Championships the intake was at its best performance. Our new design never fails and proved to be one of the most robust parts of the robot, as it took quite a beating from our own driving into walls and other robots playing defense on us.

#### The Climber

![Wings](images/frc_cad/robot2.jpg)

One secondary part of this years "end game" challenge is to lift all 3 robots on your alliance for that match 1 foot off the ground. Doing this was very difficult, though if you were able to you were granted a "ranking point", with the teams who have the most ranking points having the highest rank in competition. Being that we had a few experienced people on the team with CAD skills, we went for it. To attach ourselves to the rung that you climb from, we have an arm mounted to the back of the elevator that swings up with a detachable hook on the end of it. Once the hook is in place, the gearboxes shift into PTO and the hook detaches from the magnets holding it in place. Then, two deployable "wings" are released from the either side of the robot for our alliance members to climb onto. And finally, we climb...

![Triple Climb](images/frc_cad/triple_lift.jpg)

### Preseason Projects

For the last 2 years before the official season started, we'd use this time to develop our CAD knowledge by using new design techniques, new materials, and new assembly processes. Our preseason this year was a busy one, as we designed, machined, and assembled an elevator, custom shifting gearboxes, and a robot chassis/drivebase for everything to go on.

#### The Elevator

![Rendered Preseason Elevator](images/frc_cad/pe_render.JPG)

This elevator was a 2nd iteration of a previous cascade-style elevator I designed earlier in our previous season, looking to fix the weight and stability issues of the last one. The structure consisted of aluminum 2"x1" and 1"x1" extrusion and held together by riveted, waterjet cut aluminum gussets. Besides being actually usable on an actual robot, the cable tensioning system with turnbuckles housed inside the carriage made working on this elevator very easy. This was also the first elevator that used a bike disc brake to hold it's position under load which was a huge success.

#### The Gearboxes

![Gearbox](images/frc_cad/pgb_render.JPG)
![Gearbox](images/frc_cad/pgb_real.jpg)

These were the first "truly" custom gearboxes my team had designed, as everything about them was all designed and machined by students instead of what we did in our previous season with just making our own mounting and support plates. These gearboxes shifted into a high gearing of ~17 ft/sec and a low gear of ~2.5 ft/sec which worked great for the teleoperated and autonomous driving we put them through. Our 2018 gearboxes with a PTO were heavily based off of these gearboxes.

#### The Chassis

![Chassis](images/frc_cad/pre_chassis.JPG) 
![Another Chassis](images/frc_cad/pcu_render.JPG)

This chassis was intended to experiment with several new designs, those being inverted electronics mounting, custom shifting gearbox integration, and a new bumper layout. There are numerous minor changes on the drivetrain from our last Westcoast drive from our 2017 robot to make this one more efficient, and a stronger focus on smart electronics layout to keep most of the components close to the ground to leave room in the front and top of the robot for potential mechanisms.
