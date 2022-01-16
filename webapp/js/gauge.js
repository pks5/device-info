const Gauge = function(mOptions){
    this.m_mOptions = mOptions;

    const iWidth = 110,
            iCenter = 0.5 * iWidth,
            outerBezelWidth = iWidth * 0.009,
            innerBezelWidth = iWidth * 0.072,
            outerBezelRadius = iCenter - outerBezelWidth,
            mConstants = {
        width: iWidth,
        center: iCenter,
        outerBezelWidth: outerBezelWidth,
        outerBezelRadius: outerBezelRadius,
        innerBezelWidth: innerBezelWidth,
        innerBezelRadius: outerBezelRadius - (innerBezelWidth / 2),
        tickHeight: outerBezelWidth + innerBezelWidth + (iWidth * 0.027),
        tickWidth: iWidth * 0.009,
        tickHiderRadius: iWidth * 0.345,
        labelY: iCenter / 1.68,
        specsY: iCenter / 1.3,
        infoY: iCenter / 0.81,
        info2Y: iCenter / 0.73,
        valueLabelY: iWidth * 0.81,
        labelFontSize: iWidth * .08,
        specsFontSize: iWidth * .05,
        infoFontSize: iWidth * .05,
        valueLabelFontSize: iWidth * .12,
        needleWidth: iWidth * 0.054,
        needleCapRadius: iWidth * 0.059,
        tickSpacing: 13.5,
        lastTickAngle: 135
    };

    this.m_mConstants = mConstants;

    const elContainer = d3.select(this.m_mOptions.el),
            elChart = elContainer.append("svg").attr("preserveAspectRatio", "xMinYMin meet").attr("viewBox", "0 0 110 110");

    this.m_elContainer = elContainer;
    this.m_elChart = elChart;

      // generate the conic gradient
    const gradient = new ConicGradient({
        stops: "yellow, red, green, yellow"
    });

    const defs = elChart.append('defs');

	defs.append("pattern")
		.attr("id", "gradient")
		.attr("width", 1)
		.attr("height", 1)
	.append("image")
		.attr("width", 110)
		.attr("height", 110)
		.attr('xlink:href', gradient.dataURL);
  
        var radial_gradient = defs.append("radialGradient")
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("cx", '50%')
        .attr("cy", '50%')
        .attr("r", "75%")
        .attr("fx", '50%')
        .attr("fy", '50%')
        //.attr('gradientTransform', "translate(-200,-200)")
        .attr("id", 'gradient2');
    radial_gradient.append("stop").attr("offset", "0%").style("stop-color", "black");
    radial_gradient.append("stop").attr("offset", "65%").style("stop-color", "white");
    radial_gradient.append("stop").attr("offset", "95%").style("stop-color", "black");

    
    const needleScale = d3.scaleLinear()
      .domain([this.m_mOptions.min || 0, this.m_mOptions.max || 100])
      .range([-this.m_mConstants.lastTickAngle, this.m_mConstants.lastTickAngle]);

    this.m_fnNeedleScale = needleScale;

    const chart = this.m_elChart;

    const outerBezel = chart.append('circle')
      .attr('class', 'gaugeChart-bezel-outer')
      .attr('cx', this.m_mConstants.center)
      .attr('cy', this.m_mConstants.center)
      .attr('stroke-width', this.m_mConstants.outerBezelWidth)
      .attr('r', this.m_mConstants.outerBezelRadius);
  
    
  
    
  
      const face = chart.append('circle')
      .attr('class', 'gaugeChart-face')
      .attr('cx', this.m_mConstants.center)
      .attr('cy', this.m_mConstants.center)
      .attr('r', this.m_mConstants.outerBezelRadius - 1);

      const innerBezel = chart.append('circle')
      .attr('class', 'gaugeChart-bezel-inner')
      .attr('cx', this.m_mConstants.center)
      .attr('cy', this.m_mConstants.center)
      .attr('stroke-width', this.m_mConstants.innerBezelWidth)
      .attr('r', this.m_mConstants.innerBezelRadius)
      .attr('stroke', "url(#gradient2)");

  chart.append("path")
  .attr("transform", "translate(" + this.m_mConstants.center + "," + this.m_mConstants.center + ")")
  .attr("d", d3.arc()
    .innerRadius( 0.85*this.m_mConstants.outerBezelRadius)
    .outerRadius( this.m_mConstants.outerBezelRadius)
    .startAngle( -135 * (Math.PI/180) )
    .endAngle( 135  * (Math.PI/180))
    )
  
  .attr('fill', "url(#gradient)");

  let angle = -135;
    while (angle <= this.m_mConstants.lastTickAngle) {
      chart.append('line')
        .attr('class', 'gaugeChart-tick')
        .attr('x1', this.m_mConstants.center)
        .attr('y1', this.m_mConstants.center)
        .attr('x2', this.m_mConstants.center)
        .attr('y2', this.m_mConstants.tickHeight)
        .attr('stroke-width', this.m_mConstants.tickWidth)
        .attr('transform', `rotate(${angle} ${this.m_mConstants.center} ${this.m_mConstants.center})`);
  
      angle += this.m_mConstants.tickSpacing;
    }
  
    const tickHider = chart.append('circle')
      .attr('class', 'gaugeChart-tickHider')
      .attr('cx', this.m_mConstants.center)
      .attr('cy', this.m_mConstants.center)
      .attr('r', this.m_mConstants.tickHiderRadius);
  
    const label = chart.append('text')
      .attr('class', 'gaugeChart-label')
      .attr('x', this.m_mConstants.center)
      .attr('y', this.m_mConstants.labelY)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', this.m_mConstants.labelFontSize)
      .text(this.m_mOptions.label);

      this.m_elSpecsLabel = chart.append('text')
      .attr('class', 'gaugeChart-label-specs')
      .attr('x', this.m_mConstants.center)
      .attr('y', this.m_mConstants.specsY)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', this.m_mConstants.specsFontSize);

      this.m_elInfoLabel = chart.append('text')
      .attr('class', 'gaugeChart-label-specs')
      .attr('x', this.m_mConstants.center)
      .attr('y', this.m_mConstants.infoY)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', this.m_mConstants.infoFontSize);

      this.m_elInfo2Label = chart.append('text')
      .attr('class', 'gaugeChart-label-specs')
      .attr('x', this.m_mConstants.center)
      .attr('y', this.m_mConstants.info2Y)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', this.m_mConstants.infoFontSize);

    this.m_elValueLabel = chart.append('text')
      .attr('class', 'gaugeChart-label-value')
      .attr('x', this.m_mConstants.center)
      .attr('y', this.m_mConstants.valueLabelY)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', this.m_mConstants.valueLabelFontSize);
  
    this.m_elNeedle = chart.append("g")
          .attr('class', 'gaugeChart-needle-container')
          .style('visibility', "hidden")
          .attr('transform', `rotate(${this.m_fnNeedleScale(0)})`); 

    this.m_elNeedle.append('circle')
    .style('visibility', "hidden")
      .attr('cx', this.m_mConstants.center)
      .attr('cy', this.m_mConstants.center)
      .attr('r', 0.5*this.m_mConstants.width)

    this.m_elNeedle.append('path')
      .attr('class', 'gaugeChart-needle')
      .attr('stroke-width', this.m_mConstants.outerBezelWidth)
      
      .attr('d', `M ${this.m_mConstants.center - this.m_mConstants.needleWidth / 2} ${this.m_mConstants.center}
                  L ${this.m_mConstants.center} ${this.m_mConstants.tickHeight}
                  L ${this.m_mConstants.center + this.m_mConstants.needleWidth / 2} ${this.m_mConstants.center} Z`)
                  //.attr('transform', `rotate(${this.m_fnNeedleScale(0)} ${this.m_mConstants.center} ${this.m_mConstants.center})`)
      
      
      
  
    const needleCap = chart.append('circle')
      .attr('class', 'gaugeChart-needle-cap')
      .attr('cx', this.m_mConstants.center)
      .attr('cy', this.m_mConstants.center)
      .attr('stroke-width', this.m_mConstants.outerBezelWidth)
      .attr('r', this.m_mConstants.needleCapRadius);
};

Gauge.prototype.setSpecs = function(sSpecs){
    if(!sSpecs){
        sSpecs = "";
    }
    let sSpecsText = sSpecs;
    if(sSpecsText.length > 18){
      sSpecsText = sSpecsText.substr(0, 18) + " ...";
    }
    this.m_elSpecsLabel.text(sSpecsText).append('svg:title').text(sSpecs);

    return this;
};

Gauge.prototype.setInfo = function(sInfo, sInfo2){
  if(!sInfo){
      sInfo = "";
  }
  if(!sInfo2){
    sInfo2 = "";
}
  let sInfoText = sInfo,
    sInfo2Text = sInfo2;
  if(sInfoText.length > 18){
    sInfoText = sInfoText.substr(0, 18) + " ...";
  }

  if(sInfo2Text.length > 18){
    sInfo2Text = sInfo2Text.substr(0, 18) + " ...";
  }

  this.m_elInfoLabel.text(sInfoText).append('svg:title').text(sInfo);
  this.m_elInfo2Label.text(sInfo2Text).append('svg:title').text(sInfo2);

  return this;
};

Gauge.prototype.setValue = function(nValue){
    let sValueText = nValue;
    if(typeof nValue === 'undefined' || nValue === null || nValue === ""){
        nValue = 0;
        sValueText = "";
        this.m_elNeedle.style('visibility', "hidden");
    }
    else{
        this.m_elNeedle.style('visibility', "visible");
        sValueText += "%";
    }
    this.m_elValueLabel.text(sValueText);
    
    
    this.m_elNeedle.attr('transform', `rotate(${this.m_fnNeedleScale(nValue)})`);

    return this;
};


  