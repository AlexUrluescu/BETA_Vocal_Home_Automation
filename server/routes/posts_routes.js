import { Router } from "express";
import {
  getDataSenzors,
  getHeatingStatus,
  getTreshold,
  getSenzor,
} from "../controllers/post.controllers.js";

const router = Router();

router.get("/datasenzors", getDataSenzors);
router.get("/status", getHeatingStatus);
router.get("/treshold", getTreshold);
router.get("/senzor", getSenzor);

export default router;
