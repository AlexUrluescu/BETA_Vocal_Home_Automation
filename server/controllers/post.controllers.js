
import DataSenzors from "../models/DataSenzors.js";
import HeatingStatus from "../models/HeatingStatus.js";
import HeatingTemp from "../models/HeatingTemp.js";

let data_sezor = {};


export const getDataSenzors = async (req, res) => {
    try {    
        const data = await DataSenzors.find()
        res.send(data)
        
    } catch (error) {
        console.error(error);
        return res.status(500).json({message: error.message})
    }

};

export const getHeatingStatus = async (req, res) => {
    try {    
        const status = await HeatingStatus.find()
        res.send(status)
        
    } catch (error) {
        console.error(error);
        return res.status(500).json({message: error.message})
    }

};

export const getHeatingTemp = async (req, res) => {
    try {    
        const heating_temp = await HeatingTemp.find()
        res.send(heating_temp)
        
    } catch (error) {
        console.error(error);
        return res.status(500).json({message: error.message})
    }

};

export const changeStatus = async (req, res) => {

    try {
        const updateStatus = await HeatingStatus.findByIdAndUpdate(req.params.id, req.body, { new: true })
        console.log(updateStatus);

        if(req.body === "On"){
            return res.json({"message": "On"});
        }

        else{
            return res.json({"message": "Off"});
        }

    } catch (error) {
        return res.status(500).json({message: error.message})
        
    }
};   

export const changeHeatingTemp = async (req, res) => {

    try {
        const updateHeatingTemp = await HeatingTemp.findByIdAndUpdate(req.params.id, req.body, { new: true })
        console.log(updateHeatingTemp);
        return res.json({"message": "ok"});

    } catch (error) {
        return res.status(500).json({message: error.message})
        
    }
}; 

export const testStatus = async (req, res) => {

    try {

        const status = req.body.status;
        // console.log(status);

        const _id = req.params.id;
        // console.log(_id);

        if(status == 1){
            try {
                const updateStatus = await HeatingStatus.findByIdAndUpdate(req.params.id, req.body, { new: true });
                console.log(updateStatus);
                return res.json({"message": "On"})
                
            } catch (error) {
                console.log(error);
            }
            
        } 
        if(status == 0){
            try {
                const updateStatus = await HeatingStatus.findByIdAndUpdate(req.params.id, req.body, { new: true });
                console.log(updateStatus);
                return res.json({"message": "Off"})

            } catch (error) {
                console.log(error);
            }
            
        }

    } catch (error) {
        return res.status(500).json({message: error.message})
        
    }
};   



export const datasenzor = async (req, res) => {
    const data = req.body;

    data_sezor = data

    // Procesați datele primite cum doriți
    // Exemplu: Salvare într-o bază de date, trimitere notificări, etc.
  
    // Răspuns către scriptul de pe Raspberry Pi pentru a indica succesul preluării datelor
    const response = {
      message: 'Datele de la senzori au fost primite cu succes!',
      body: data
    };
  
    res.json(response);
}

export const getSenzor = async (req, res) => {
    try {
        res.send(data_sezor)
        
    } catch (error) {
        console.log(error);
    }
}
