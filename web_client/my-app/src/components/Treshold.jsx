import React from "react";

const Treshold = ({
  isToggled,
  tempHome,
  heatingTemp,
  classStyle1,
  classStyle2,
  text,
}) => {
  return (
    <div>
      <div
        className={
          isToggled === true && tempHome < heatingTemp
            ? classStyle1 
            : classStyle2
        }
      >
        {/* {heatingTemp} <sup className="text-lg">{text}</sup> */}
        <h2 className="text-6xl ml-4">{heatingTemp}<sup className="text-3xl font-semibold ml-4">{text}</sup></h2>
      </div>
    </div>
  );
};

export default Treshold;
