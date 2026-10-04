import { motion } from "framer-motion";

export default function StatsCard({
    title,
    value,
    icon: Icon,
    color="#5b8d89",
    subtitle="All time"
}){

    return(

        <motion.div
            className="stats-card"
            initial={{opacity:0,y:20}}
            animate={{opacity:1,y:0}}
            transition={{duration:.35}}
        >

            <div className="stats-header">

                <div
                    className="stats-icon"
                    style={{background:color}}
                >

                    <Icon size={20}/>

                </div>

                <span className="stats-title">

                    {title}

                </span>

            </div>

            <h2 className="stats-value">

                {value}

            </h2>

            <div className="stats-footer"><span className="stats-period">{subtitle}</span></div>

        </motion.div>

    )

}
