


def silver_silver_chloride_to_RHE(pH):
    """
    calculate RE vs RHE for Ag/AgCl reference electrode

    based on formula:
    E(RHE) = E(Ag/AgCl) + E0(Ag/AgCl) + 0.059pH
    where E0(Ag/AgCl) = 0.1976
    """
    
    return 0.1976 + 0.059*pH